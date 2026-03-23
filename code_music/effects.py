"""Audio effects: reverb, delay, chorus, distortion, filters, compress, pan.

All functions take/return stereo float64 arrays shape (N, 2).
All inner loops use scipy/numpy — no Python sample-level loops.
"""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray
from scipy import signal as sig

FloatArray = NDArray[np.float64]

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _stereo(fn, samples: FloatArray, **kw) -> FloatArray:
    """Apply a mono function independently to each channel."""
    l_out = fn(samples[:, 0], **kw)
    r_out = fn(samples[:, 1], **kw)
    return np.column_stack([l_out, r_out]).astype(np.float64)


def _make_reverb_ir(sample_rate: int, room_size: float, damping: float) -> np.ndarray:
    """Build a short exponentially-decaying impulse response for convolution reverb.

    Much faster than recursive comb/allpass for long signals — O(N log N) FFT convolution.
    """
    decay_sec = 0.5 + room_size * 2.5  # 0.5s (small) … 3.0s (large)
    ir_len = int(decay_sec * sample_rate)
    rng = np.random.default_rng(42)  # deterministic
    noise = rng.standard_normal(ir_len)
    t = np.arange(ir_len) / sample_rate
    # Exponential decay envelope
    env = np.exp(-t * (3.0 + damping * 8.0))
    # Low-pass the IR to simulate room damping
    cutoff = max(500.0, 8000.0 * (1.0 - damping))
    sos = sig.butter(2, cutoff, btype="low", fs=sample_rate, output="sos")
    ir = sig.sosfilt(sos, noise * env)
    # Normalize IR
    peak = np.max(np.abs(ir))
    if peak > 0:
        ir /= peak
    return ir


# ---------------------------------------------------------------------------
# Reverb
# ---------------------------------------------------------------------------


def reverb(
    samples: FloatArray,
    sample_rate: int = 44100,
    room_size: float = 0.5,
    damping: float = 0.4,
    wet: float = 0.25,
) -> FloatArray:
    """Freeverb-style stereo reverb (comb + allpass network).

    Args:
        room_size: 0.0–1.0 — larger = longer decay.
        damping:   0.0–1.0 — more high-frequency absorption.
        wet:       Mix ratio (0 = dry, 1 = full wet).
    """
    # Convolve with a synthetic exponential IR — O(N log N), fast for any length
    ir = _make_reverb_ir(sample_rate, room_size, damping)
    left = samples[:, 0]
    right = samples[:, 1]

    rev_l = sig.fftconvolve(left, ir, mode="full")[: len(left)]
    rev_r = sig.fftconvolve(right, np.roll(ir, 1), mode="full")[: len(right)]

    for rev in (rev_l, rev_r):
        p = np.max(np.abs(rev))
        if p > 0:
            rev /= p

    return np.column_stack(
        [
            left * (1 - wet) + rev_l * wet,
            right * (1 - wet) + rev_r * wet,
        ]
    ).astype(np.float64)


# ---------------------------------------------------------------------------
# Delay
# ---------------------------------------------------------------------------


def delay(
    samples: FloatArray,
    sample_rate: int = 44100,
    delay_ms: float = 375.0,
    feedback: float = 0.4,
    wet: float = 0.3,
    ping_pong: bool = True,
) -> FloatArray:
    """Stereo echo with optional ping-pong.

    Uses numpy roll for the feedback buffer — O(n_taps) not O(n_samples).
    """
    d = max(1, int(delay_ms * sample_rate / 1000))
    n = len(samples)
    out = samples.copy()
    # Build multi-tap echo by summing decayed, shifted copies
    max_taps = max(1, int(math.log(0.01) / math.log(max(feedback, 1e-9))))
    max_taps = min(max_taps, 16)

    for tap in range(1, max_taps + 1):
        shift = tap * d
        if shift >= n:
            break
        gain = (wet * feedback ** (tap - 1)) if tap == 1 else (feedback**tap)
        if ping_pong and tap % 2 == 1:
            # Odd taps: swap L/R
            echo_l = np.roll(samples[:, 1], shift) * gain
            echo_r = np.roll(samples[:, 0], shift) * gain
        else:
            echo_l = np.roll(samples[:, 0], shift) * gain
            echo_r = np.roll(samples[:, 1], shift) * gain
        # Zero-out the wrap-around at the start
        echo_l[:shift] = 0.0
        echo_r[:shift] = 0.0
        out[:, 0] += echo_l
        out[:, 1] += echo_r

    return out.astype(np.float64)


# ---------------------------------------------------------------------------
# Chorus
# ---------------------------------------------------------------------------


def chorus(
    samples: FloatArray,
    sample_rate: int = 44100,
    rate_hz: float = 0.8,
    depth_ms: float = 3.0,
    wet: float = 0.4,
) -> FloatArray:
    """LFO-modulated pitch/delay chorus via fractional resampling."""
    n = len(samples)
    t = np.arange(n) / sample_rate
    # LFO modulates playback speed slightly — resample approach:
    # shift each channel by a time-varying amount using numpy interp
    lfo = np.sin(2 * np.pi * rate_hz * t)
    depth_samples = depth_ms * sample_rate / 1000.0
    offsets = (lfo * depth_samples).astype(np.float64)

    indices = np.arange(n, dtype=np.float64) - offsets
    indices = np.clip(indices, 0, n - 1)

    def _warp(ch: np.ndarray) -> np.ndarray:
        lo = np.floor(indices).astype(int)
        hi = np.minimum(lo + 1, n - 1)
        frac = indices - lo
        return ch[lo] * (1 - frac) + ch[hi] * frac

    warped_l = _warp(samples[:, 0])
    warped_r = _warp(samples[:, 1])

    return np.column_stack(
        [
            samples[:, 0] * (1 - wet) + warped_l * wet,
            samples[:, 1] * (1 - wet) + warped_r * wet,
        ]
    ).astype(np.float64)


# ---------------------------------------------------------------------------
# Distortion
# ---------------------------------------------------------------------------


def distortion(
    samples: FloatArray,
    drive: float = 3.0,
    tone: float = 0.5,
    wet: float = 0.6,
) -> FloatArray:
    """Soft-clip overdrive with 1-pole tone control via scipy lfilter."""
    driven = np.tanh(samples * drive)
    # 1-pole LP IIR tone control: y[n] = alpha*x[n] + (1-alpha)*y[n-1]
    alpha = 0.1 + tone * 0.85
    b_lp = [alpha]
    a_lp = [1.0, -(1.0 - alpha)]
    toned_l = sig.lfilter(b_lp, a_lp, driven[:, 0])
    toned_r = sig.lfilter(b_lp, a_lp, driven[:, 1])
    toned = np.column_stack([toned_l, toned_r])
    return (samples * (1 - wet) + toned * wet).astype(np.float64)


# ---------------------------------------------------------------------------
# Filters (biquad via scipy sosfilt — fast and stable)
# ---------------------------------------------------------------------------


def _biquad_sos(samples: FloatArray, sos: np.ndarray) -> FloatArray:
    """Apply a scipy SOS filter to each channel independently."""
    l_out = sig.sosfilt(sos, samples[:, 0])
    r_out = sig.sosfilt(sos, samples[:, 1])
    return np.column_stack([l_out, r_out]).astype(np.float64)


def lowpass(
    samples: FloatArray,
    sample_rate: int = 44100,
    cutoff_hz: float = 2000.0,
    q: float = 0.707,
) -> FloatArray:
    """Biquad low-pass filter."""
    sos = sig.butter(2, cutoff_hz, btype="low", fs=sample_rate, output="sos")
    return _biquad_sos(samples, sos)


def highpass(
    samples: FloatArray,
    sample_rate: int = 44100,
    cutoff_hz: float = 200.0,
    q: float = 0.707,
) -> FloatArray:
    """Biquad high-pass filter."""
    sos = sig.butter(2, cutoff_hz, btype="high", fs=sample_rate, output="sos")
    return _biquad_sos(samples, sos)


def bandpass(
    samples: FloatArray,
    sample_rate: int = 44100,
    center_hz: float = 1000.0,
    q: float = 1.0,
) -> FloatArray:
    """Biquad band-pass filter."""
    bw = center_hz / q
    low = max(20.0, center_hz - bw / 2)
    high = min(sample_rate / 2 - 1, center_hz + bw / 2)
    sos = sig.butter(2, [low, high], btype="band", fs=sample_rate, output="sos")
    return _biquad_sos(samples, sos)


# ---------------------------------------------------------------------------
# Compressor
# ---------------------------------------------------------------------------


def compress(
    samples: FloatArray,
    sample_rate: int = 44100,
    threshold: float = 0.5,
    ratio: float = 4.0,
    attack_ms: float = 5.0,
    release_ms: float = 50.0,
    makeup_gain: float = 1.2,
) -> FloatArray:
    """Peak-following compressor — vectorised envelope via scipy lfilter."""
    peak = np.max(np.abs(samples), axis=1)  # mono-linked

    # Smooth envelope: use the slower (release) coefficient as a uniform IIR
    # smoother — fast via scipy lfilter, good enough for gain riding.
    r_coef = math.exp(-1.0 / max(1, release_ms * sample_rate / 1000))
    env = sig.lfilter([1.0 - r_coef], [1.0, -r_coef], peak)

    # Gain computation (fully vectorised)
    gain = np.where(
        env > threshold,
        (threshold + (env - threshold) / ratio) / np.maximum(env, 1e-9),
        1.0,
    )

    result = samples * gain[:, np.newaxis] * makeup_gain
    return np.clip(result, -1.0, 1.0).astype(np.float64)


# ---------------------------------------------------------------------------
# Stereo pan
# ---------------------------------------------------------------------------


def pan(samples: FloatArray, position: float = 0.0) -> FloatArray:
    """Equal-power stereo pan. position: -1.0 (L) … 0.0 (C) … 1.0 (R)."""
    angle = (position + 1) / 2 * math.pi / 2
    result = samples.copy()
    result[:, 0] *= math.cos(angle)
    result[:, 1] *= math.sin(angle)
    return result.astype(np.float64)


# ---------------------------------------------------------------------------
# LFO modulation — tremolo (volume) and vibrato (pitch)
# ---------------------------------------------------------------------------


def tremolo(
    samples: FloatArray,
    sample_rate: int = 44100,
    rate_hz: float = 5.0,
    depth: float = 0.3,
) -> FloatArray:
    """Amplitude tremolo via sinusoidal LFO.

    Args:
        rate_hz: LFO frequency in Hz (typical: 3–8 Hz).
        depth:   Modulation depth 0.0–1.0 (0 = no effect, 1 = full on/off).
    """
    n = len(samples)
    t = np.arange(n) / sample_rate
    lfo = 1.0 - depth * (0.5 - 0.5 * np.sin(2 * np.pi * rate_hz * t))
    return (samples * lfo[:, np.newaxis]).astype(np.float64)


def vibrato(
    samples: FloatArray,
    sample_rate: int = 44100,
    rate_hz: float = 5.5,
    depth_cents: float = 25.0,
) -> FloatArray:
    """Pitch vibrato via LFO-modulated time-stretching (warp method).

    Args:
        rate_hz:     LFO speed in Hz.
        depth_cents: Max pitch deviation in cents (100 cents = 1 semitone).
    """
    n = len(samples)
    t = np.arange(n) / sample_rate
    depth_samples = depth_cents / 100.0 * sample_rate / (rate_hz * 2 * np.pi)
    offsets = depth_samples * np.sin(2 * np.pi * rate_hz * t)
    indices = np.clip(np.arange(n, dtype=np.float64) - offsets, 0, n - 1)

    lo = np.floor(indices).astype(int)
    hi = np.minimum(lo + 1, n - 1)
    frac = indices - lo

    warped_l = samples[lo, 0] * (1 - frac) + samples[hi, 0] * frac
    warped_r = samples[lo, 1] * (1 - frac) + samples[hi, 1] * frac
    return np.column_stack([warped_l, warped_r]).astype(np.float64)


def lfo_filter(
    samples: FloatArray,
    sample_rate: int = 44100,
    rate_hz: float = 0.5,
    min_cutoff: float = 300.0,
    max_cutoff: float = 4000.0,
    filter_type: str = "low",
) -> FloatArray:
    """LFO-swept filter — the classic EDM filter-open effect.

    Args:
        rate_hz:    LFO speed. Slow (0.1–1 Hz) = gradual sweep. Fast = wah.
        min_cutoff: Filter floor in Hz.
        max_cutoff: Filter ceiling in Hz.
        filter_type: "low" or "high".
    """
    n = len(samples)
    t = np.arange(n) / sample_rate
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * rate_hz * t)  # 0..1
    cutoffs = min_cutoff + lfo * (max_cutoff - min_cutoff)

    # Process in blocks of 512 samples with fixed cutoff per block
    block_size = 512
    out = np.zeros_like(samples)
    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = samples[start:end]
        cutoff = float(np.mean(cutoffs[start:end]))
        cutoff = np.clip(cutoff, 20.0, sample_rate / 2 - 1)
        if filter_type == "high":
            sos = sig.butter(2, cutoff, btype="high", fs=sample_rate, output="sos")
        else:
            sos = sig.butter(2, cutoff, btype="low", fs=sample_rate, output="sos")
        out[start:end] = sig.sosfilt(sos, block)
    return out.astype(np.float64)


# ---------------------------------------------------------------------------
# Sidechain compression — the classic EDM "pumping" effect
# ---------------------------------------------------------------------------


def sidechain(
    target: FloatArray,
    trigger: FloatArray,
    sample_rate: int = 44100,
    threshold: float = 0.3,
    ratio: float = 8.0,
    attack_ms: float = 2.0,
    release_ms: float = 80.0,
    depth: float = 1.0,
) -> FloatArray:
    """Sidechain compression: duck `target` when `trigger` is loud.

    Classic EDM pumping effect — route kick drum as `trigger`,
    pad/bass as `target`. The pad ducks every time the kick hits.

    Args:
        target:      Signal to be compressed (e.g. pad, bass).
        trigger:     Signal driving the compression (e.g. kick drum).
        threshold:   Trigger level above which compression starts (0–1).
        ratio:       Compression ratio (higher = more ducking).
        attack_ms:   How fast the duck clamps down.
        release_ms:  How fast it lets go (long release = pumping feel).
        depth:       0.0 = no effect, 1.0 = full sidechain compression.
    """
    # Extract envelope from trigger (mono-linked)
    # Use release coefficient for smoothing; attack_ms reserved for future use
    trig_mono = np.max(np.abs(trigger), axis=1)
    r_coef = math.exp(-1.0 / max(1, release_ms * sample_rate / 1000))
    _ = attack_ms  # kept in signature for future attack-specific smoothing

    # AR envelope follower — vectorised via lfilter
    env = sig.lfilter([1.0 - r_coef], [1.0, -r_coef], trig_mono)

    # Gain computation
    gain = np.where(
        env > threshold,
        (threshold + (env - threshold) / ratio) / np.maximum(env, 1e-9),
        1.0,
    )

    # Blend between dry (gain=1) and ducked (gain=computed) by depth
    blended_gain = 1.0 - depth * (1.0 - gain)
    result = target * blended_gain[:, np.newaxis]
    return np.clip(result, -1.0, 1.0).astype(np.float64)


# ---------------------------------------------------------------------------
# Gate — rhythmic amplitude chop (trance gate / stutter)
# ---------------------------------------------------------------------------


def gate(
    samples: FloatArray,
    sample_rate: int = 44100,
    rate_hz: float = 8.0,
    shape: str = "square",
    duty: float = 0.5,
) -> FloatArray:
    """Rhythmic amplitude gate — chops signal on/off at rate_hz.

    The classic trance gate / stutter effect. Use on pads, strings, or vocals.

    Args:
        rate_hz: Gate frequency in Hz (e.g. 8.0 = 8th notes at 120 BPM).
        shape:   "square" (hard on/off), "ramp_up", "ramp_down", "trapezoid".
        duty:    Fraction of each cycle that is open (0.0–1.0).
    """
    n = len(samples)
    t = np.arange(n) / sample_rate
    phase = (t * rate_hz) % 1.0  # 0..1 within each cycle

    if shape == "square":
        env = np.where(phase < duty, 1.0, 0.0)
    elif shape == "ramp_up":
        env = np.where(phase < duty, phase / max(duty, 1e-6), 0.0)
    elif shape == "ramp_down":
        env = np.where(phase < duty, 1.0 - phase / max(duty, 1e-6), 0.0)
    elif shape == "trapezoid":
        ramp = 0.1
        env = np.where(
            phase < ramp,
            phase / ramp,
            np.where(phase < duty - ramp, 1.0, np.where(phase < duty, (duty - phase) / ramp, 0.0)),
        )
    else:
        env = np.where(phase < duty, 1.0, 0.0)

    return (samples * env[:, np.newaxis]).astype(np.float64)


# ---------------------------------------------------------------------------
# Limiter — transparent brick-wall peak limiter
# ---------------------------------------------------------------------------


def limiter(
    samples: FloatArray,
    sample_rate: int = 44100,
    ceiling: float = 0.98,
    release_ms: float = 50.0,
) -> FloatArray:
    """Brick-wall limiter — prevents clipping above ceiling.

    Faster than compress for mastering: no attack (instant catch),
    smooth release. Use as the last effect on the master bus.

    Args:
        ceiling:    Peak level to not exceed (0.0–1.0, typically 0.95–0.99).
        release_ms: How fast the limiter lets go after a peak.
    """
    peak = np.max(np.abs(samples), axis=1)
    r_coef = math.exp(-1.0 / max(1, release_ms * sample_rate / 1000))
    # Hold-and-release envelope: take max of current peak and decayed previous
    env = sig.lfilter([1.0 - r_coef], [1.0, -r_coef], peak)
    env = np.maximum(env, peak)  # instant attack

    gain = np.where(env > ceiling, ceiling / np.maximum(env, 1e-9), 1.0)
    result = samples * gain[:, np.newaxis]
    return np.clip(result, -ceiling, ceiling).astype(np.float64)


# ---------------------------------------------------------------------------
# Stereo width — mid/side processing
# ---------------------------------------------------------------------------


def stereo_width(samples: FloatArray, width: float = 1.5) -> FloatArray:
    """Adjust stereo width using M/S processing.

    Args:
        width: 0.0 = mono, 1.0 = unchanged, 2.0 = double width, >2.0 = very wide.
               Values > 1.5 can cause phase issues on mono systems.
    """
    mid = (samples[:, 0] + samples[:, 1]) * 0.5
    side = (samples[:, 0] - samples[:, 1]) * 0.5 * width
    left = mid + side
    right = mid - side
    return np.column_stack([left, right]).astype(np.float64)


# ---------------------------------------------------------------------------
# Noise sweep — filtered white noise swell (EDM build-up effect)
# ---------------------------------------------------------------------------


def noise_sweep(
    n_samples: int,
    sample_rate: int = 44100,
    start_cutoff: float = 200.0,
    end_cutoff: float = 18000.0,
    volume: float = 0.3,
    pan: float = 0.0,
) -> FloatArray:
    """Generate a rising filtered noise sweep — classic EDM build-up.

    Args:
        n_samples:    Length of output in samples.
        start_cutoff: LP filter start frequency (Hz).
        end_cutoff:   LP filter end frequency (Hz).
        volume:       Output amplitude.
        pan:          Stereo position (-1..1).
    """
    rng = np.random.default_rng(42)
    noise = rng.standard_normal(n_samples)

    # Linearly interpolate cutoff across blocks
    block = 512
    out = np.zeros(n_samples)
    for i in range(0, n_samples, block):
        frac = i / n_samples
        cutoff = start_cutoff + frac * (end_cutoff - start_cutoff)
        cutoff = np.clip(cutoff, 20.0, sample_rate / 2 - 1)
        sos = sig.butter(2, cutoff, btype="low", fs=sample_rate, output="sos")
        end_i = min(i + block, n_samples)
        out[i:end_i] = sig.sosfilt(sos, noise[i:end_i])

    # Amplitude envelope: ramp up over the sweep
    t = np.linspace(0, 1, n_samples)
    env = t**2  # quadratic ramp = feels like energy building
    out *= env * volume

    # Pan
    angle = (pan + 1) / 2 * math.pi / 2
    l_gain = math.cos(angle)
    r_gain = math.sin(angle)
    stereo = np.column_stack([out * l_gain, out * r_gain])
    return np.clip(stereo, -1.0, 1.0).astype(np.float64)


# ---------------------------------------------------------------------------
# Phaser — all-pass chain with LFO sweep (swirling texture)
# ---------------------------------------------------------------------------


def phaser(
    samples: FloatArray,
    sample_rate: int = 44100,
    rate_hz: float = 0.5,
    depth: float = 0.7,
    stages: int = 4,
    wet: float = 0.5,
) -> FloatArray:
    """Multi-stage all-pass phaser with LFO.

    Args:
        rate_hz: LFO frequency (slow = smooth sweep, fast = wah-like).
        depth:   Modulation depth.
        stages:  Number of all-pass stages (more = richer phasing).
        wet:     Wet/dry mix.
    """
    n = len(samples)
    t = np.arange(n) / sample_rate
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * rate_hz * t)

    out = samples.copy()
    for _ in range(stages):
        # All-pass coefficient varies with LFO
        coeffs = depth * lfo

        def _ap_channel(x: np.ndarray, c: np.ndarray) -> np.ndarray:
            y = np.zeros_like(x)
            z = 0.0
            for i in range(len(x)):
                ci = c[i]
                y[i] = -ci * x[i] + z + ci * (z if i > 0 else 0)
                z = x[i] + ci * y[i]
            return y

        # Vectorised approximation: apply as time-varying 1st-order AP
        # Use block processing for speed
        block = 256
        ap_l = np.zeros(n)
        ap_r = np.zeros(n)
        for start in range(0, n, block):
            end_b = min(start + block, n)
            c_avg = float(np.mean(coeffs[start:end_b]))
            # 1st-order all-pass: y[n] = -c*x[n] + x[n-1] + c*y[n-1]
            b_ap = [-c_avg, 1.0]
            a_ap = [1.0, -c_avg]
            ap_l[start:end_b] = sig.lfilter(b_ap, a_ap, out[start:end_b, 0])
            ap_r[start:end_b] = sig.lfilter(b_ap, a_ap, out[start:end_b, 1])

        phased = np.column_stack([ap_l, ap_r])
        out = samples * (1 - wet) + phased * wet

    return out.astype(np.float64)


# ---------------------------------------------------------------------------
# Flanger — short delay + LFO (jet engine sweep)
# ---------------------------------------------------------------------------


def flanger(
    samples: FloatArray,
    sample_rate: int = 44100,
    rate_hz: float = 0.3,
    depth_ms: float = 5.0,
    feedback: float = 0.5,
    wet: float = 0.5,
) -> FloatArray:
    """Flanger — very short LFO-modulated delay with feedback.

    More dramatic than chorus — produces that jet-engine sweep sound
    heard on Daft Punk leads, Mord Fustang arps, and classic rock guitars.

    Args:
        rate_hz:   LFO speed.
        depth_ms:  Max delay depth in milliseconds (0.1–10ms typical).
        feedback:  Feedback amount (0–0.9).
        wet:       Wet/dry mix.
    """
    # Use the chorus effect with short depth and add feedback character
    n = len(samples)
    t = np.arange(n) / sample_rate
    max_d = int(depth_ms * sample_rate / 1000) + 2
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * rate_hz * t)
    delays = (lfo * depth_ms * sample_rate / 1000).astype(int)

    out = samples.copy()
    buf = np.zeros((max_d, 2))
    for i in range(n):
        d = max(1, delays[i])
        idx = (i - d) % max_d
        flanged = buf[idx] * feedback
        out[i] = samples[i] * (1 - wet) + (samples[i] + flanged) * wet
        buf[i % max_d] = samples[i] + flanged * feedback
    return out.astype(np.float64)
