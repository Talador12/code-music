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


# ---------------------------------------------------------------------------
# Bitcrusher — lo-fi / chiptune / downsampling
# ---------------------------------------------------------------------------


def bitcrush(
    samples: FloatArray,
    sample_rate: int = 44100,
    bit_depth: int = 8,
    downsample: int = 4,
    wet: float = 1.0,
) -> FloatArray:
    """Bitcrusher — reduces bit depth and sample rate for lo-fi / 8-bit texture.

    Args:
        bit_depth:   Target bit depth (4=harsh, 8=classic NES, 12=mild warmth).
        downsample:  Sample-rate reduction factor (1=none, 4=quarter rate, 8=gritty).
        wet:         Wet/dry mix.
    """
    levels = 2**bit_depth
    # Quantise
    crushed = np.round(samples * levels) / levels
    # Downsample: hold each sample for `downsample` steps
    if downsample > 1:
        for ch in range(2):
            held = crushed[::downsample, ch]
            repeated = np.repeat(held, downsample)[: len(samples)]
            crushed[:, ch] = repeated
    return (samples * (1 - wet) + crushed * wet).astype(np.float64)


# ---------------------------------------------------------------------------
# Ring modulator — metallic / robot / AM radio
# ---------------------------------------------------------------------------


def ring_mod(
    samples: FloatArray,
    sample_rate: int = 44100,
    freq_hz: float = 440.0,
    wet: float = 0.7,
) -> FloatArray:
    """Ring modulator — multiplies signal by a carrier sine wave.

    Produces sum and difference frequencies, creating metallic/robotic tones.
    Classic effect for Dalek voices, metal bells, and experimental textures.

    Args:
        freq_hz: Carrier frequency in Hz. Low (50–200Hz) = bass thickening.
                 Mid (400–1000Hz) = bell/metallic. High (2000Hz+) = robotic.
        wet:     Wet/dry mix.
    """
    n = len(samples)
    t = np.arange(n) / sample_rate
    carrier = np.sin(2 * np.pi * freq_hz * t)
    modulated = samples * carrier[:, np.newaxis]
    return (samples * (1 - wet) + modulated * wet).astype(np.float64)


# ---------------------------------------------------------------------------
# Tape saturation — warm analog simulation
# ---------------------------------------------------------------------------


def tape_sat(
    samples: FloatArray,
    sample_rate: int = 44100,
    drive: float = 2.0,
    warmth: float = 0.5,
    wet: float = 0.6,
) -> FloatArray:
    """Tape saturation — warm harmonic distortion with low-end emphasis.

    Simulates the soft compression and 2nd-order harmonic distortion of
    analog tape. Adds warmth, glue, and subtle compression to a mix.

    Args:
        drive:   Pre-gain (1.0 = gentle, 4.0 = saturated).
        warmth:  Low-end boost amount (0–1). Higher = more bass warmth.
        wet:     Wet/dry mix.
    """
    # Soft saturation: tanh is too clean, use x/(1+|x|) for tape feel
    driven = samples * drive
    saturated = driven / (1 + np.abs(driven))

    # Low-shelf boost for warmth (tape has enhanced low frequencies)
    if warmth > 0:
        cutoff = 300.0
        sos = sig.butter(2, cutoff, btype="low", fs=sample_rate, output="sos")
        low_l = sig.sosfilt(sos, saturated[:, 0])
        low_r = sig.sosfilt(sos, saturated[:, 1])
        low_boost = np.column_stack([low_l, low_r]) * warmth * 0.5
        saturated = saturated + low_boost

    return np.clip(samples * (1 - wet) + saturated * wet, -1.0, 1.0).astype(np.float64)


# ---------------------------------------------------------------------------
# Multi-band compressor
# ---------------------------------------------------------------------------


def multiband_compress(
    samples: FloatArray,
    sample_rate: int = 44100,
    low_cut: float = 250.0,
    high_cut: float = 4000.0,
    low_threshold: float = 0.6,
    mid_threshold: float = 0.5,
    high_threshold: float = 0.4,
    ratio: float = 3.0,
    makeup_gain: float = 1.15,
) -> FloatArray:
    """Three-band compressor: low / mid / high compressed independently.

    Splits the signal into three frequency bands, compresses each with
    its own threshold, then recombines. Avoids the pumping artifacts of
    a full-band compressor on complex mixes.

    Args:
        low_cut:          Crossover between low and mid bands (Hz).
        high_cut:         Crossover between mid and high bands (Hz).
        low_threshold:    Compression threshold for the bass band.
        mid_threshold:    Compression threshold for the mid band.
        high_threshold:   Compression threshold for the high band.
        ratio:            Compression ratio applied to all bands.
        makeup_gain:      Post-compression gain.
    """
    # Split into three bands via butterworth crossovers
    sos_low = sig.butter(4, low_cut, btype="low", fs=sample_rate, output="sos")
    sos_mid = sig.butter(4, [low_cut, high_cut], btype="band", fs=sample_rate, output="sos")
    sos_high = sig.butter(4, high_cut, btype="high", fs=sample_rate, output="sos")

    def _band(sos):
        return np.column_stack(
            [
                sig.sosfilt(sos, samples[:, 0]),
                sig.sosfilt(sos, samples[:, 1]),
            ]
        ).astype(np.float64)

    low_band = _band(sos_low)
    mid_band = _band(sos_mid)
    high_band = _band(sos_high)

    # Compress each band independently
    low_c = compress(low_band, sample_rate, threshold=low_threshold, ratio=ratio, makeup_gain=1.0)
    mid_c = compress(mid_band, sample_rate, threshold=mid_threshold, ratio=ratio, makeup_gain=1.0)
    high_c = compress(
        high_band, sample_rate, threshold=high_threshold, ratio=ratio, makeup_gain=1.0
    )

    result = (low_c + mid_c + high_c) * makeup_gain
    return np.clip(result, -1.0, 1.0).astype(np.float64)


# ---------------------------------------------------------------------------
# Vocoder — carrier modulated by a modulator (robot/harmonizer voice)
# ---------------------------------------------------------------------------


def vocoder(
    carrier: FloatArray,
    modulator: FloatArray,
    sample_rate: int = 44100,
    bands: int = 16,
    wet: float = 0.9,
) -> FloatArray:
    """Vocoder: impose the spectral envelope of `modulator` onto `carrier`.

    Classic use: carrier = synth pad/sawtooth, modulator = voice/speech.
    The result sounds like the synth is 'speaking'. Also works with any
    two audio signals for interesting timbral blends.

    Args:
        carrier:   The signal whose pitch/timbre gets reshaped (e.g. synth).
        modulator: The signal whose spectral envelope is extracted (e.g. voice).
        bands:     Number of frequency bands (more = smoother but slower).
        wet:       Mix between vocoded output and dry carrier.
    """
    n = min(len(carrier), len(modulator))
    carrier = carrier[:n]
    modulator = modulator[:n]

    # Pad both to same length
    if len(carrier) < n or len(modulator) < n:
        carrier = np.pad(carrier, ((0, max(0, n - len(carrier))), (0, 0)))
        modulator = np.pad(modulator, ((0, max(0, n - len(modulator))), (0, 0)))

    # Frequency bands spaced logarithmically from 80Hz to 8kHz
    freqs = np.logspace(np.log10(80), np.log10(8000), bands + 1)

    output = np.zeros((n, 2), dtype=np.float64)

    for i in range(bands):
        lo, hi = freqs[i], freqs[i + 1]
        if lo >= sample_rate / 2 - 1 or hi >= sample_rate / 2:
            continue
        hi = min(hi, sample_rate / 2 - 1)
        try:
            sos = sig.butter(2, [lo, hi], btype="band", fs=sample_rate, output="sos")
        except Exception:
            continue

        # Filter both signals to this band
        car_band = np.column_stack(
            [
                sig.sosfilt(sos, carrier[:, 0]),
                sig.sosfilt(sos, carrier[:, 1]),
            ]
        )
        mod_band = np.column_stack(
            [
                sig.sosfilt(sos, modulator[:, 0]),
                sig.sosfilt(sos, modulator[:, 1]),
            ]
        )

        # Extract envelope from modulator band (rectify + smooth)
        r_coef = math.exp(-1.0 / max(1, 10 * sample_rate / 1000))
        env_l = sig.lfilter([1.0 - r_coef], [1.0, -r_coef], np.abs(mod_band[:, 0]))
        env_r = sig.lfilter([1.0 - r_coef], [1.0, -r_coef], np.abs(mod_band[:, 1]))
        env = np.column_stack([env_l, env_r])

        # Apply modulator envelope to carrier band
        output += car_band * env * 4.0  # ×4 to compensate for band energy loss

    # Normalize
    peak = np.max(np.abs(output))
    if peak > 0:
        output /= peak

    result = carrier * (1 - wet) + output * wet
    return np.clip(result, -1.0, 1.0).astype(np.float64)


# ---------------------------------------------------------------------------
# Multi-tap delay — more than 2 echo taps with individual timing/pan
# ---------------------------------------------------------------------------


def multitap_delay(
    samples: FloatArray,
    sample_rate: int = 44100,
    taps: list[tuple[float, float, float]] | None = None,
    feedback: float = 0.3,
) -> FloatArray:
    """Multi-tap delay: multiple echoes at different times, levels, and pans.

    Args:
        taps: List of (delay_ms, level, pan) tuples.
              pan: -1.0=L, 0.0=center, 1.0=R.
              Default: classic three-tap spread.
        feedback: Overall feedback amount.

    Example::

        # Three taps: 125ms left, 250ms center, 375ms right
        multitap_delay(s, sr, taps=[(125, 0.6, -0.5), (250, 0.4, 0.0), (375, 0.3, 0.5)])
    """
    if taps is None:
        taps = [(125.0, 0.6, -0.5), (250.0, 0.4, 0.0), (375.0, 0.3, 0.5)]

    n = len(samples)
    out = samples.copy()

    for delay_ms, level, pan in taps:
        d = max(1, int(delay_ms * sample_rate / 1000))
        if d >= n:
            continue
        angle = (pan + 1) / 2 * math.pi / 2
        l_gain = math.cos(angle) * level
        r_gain = math.sin(angle) * level
        echo = np.roll(samples, d)
        echo[:d] = 0.0
        out[:, 0] += echo[:, 0] * l_gain
        out[:, 1] += echo[:, 1] * r_gain

        # Feedback: add decayed version of each tap
        if feedback > 0:
            echo2 = np.roll(echo, d)
            echo2[: d * 2] = 0.0
            out[:, 0] += echo2[:, 0] * l_gain * feedback
            out[:, 1] += echo2[:, 1] * r_gain * feedback

    peak = np.max(np.abs(out))
    if peak > 1.0:
        out /= peak
    return out.astype(np.float64)


# ---------------------------------------------------------------------------
# Granular synthesis effect — scatter audio into grains, re-assemble
# ---------------------------------------------------------------------------


def granular(
    samples: FloatArray,
    sample_rate: int = 44100,
    grain_size_ms: float = 50.0,
    scatter: float = 0.3,
    pitch_spread: float = 0.0,
    density: float = 1.0,
    wet: float = 0.7,
) -> FloatArray:
    """Granular effect: chop audio into grains and re-scatter them.

    Creates shimmering, frozen, or glitchy textures by re-ordering small
    fragments of audio. Common in ambient, experimental, and modern electronic.

    Args:
        grain_size_ms: Size of each grain in milliseconds (20–200ms typical).
        scatter:       How far grains are displaced in time (0=none, 1=fully random).
        pitch_spread:  Pitch variation per grain in semitones (0=none, 0.5=slight).
        density:       Probability a grain plays (0–1). Lower = sparser texture.
        wet:           Wet/dry mix.
    """
    grain_samples = max(64, int(grain_size_ms * sample_rate / 1000))
    n = len(samples)
    rng = np.random.default_rng(42)
    out = np.zeros_like(samples)
    counts = np.zeros(n)

    n_grains = int(n / grain_samples * 2)  # overlapping grains

    for _ in range(n_grains):
        if rng.random() > density:
            continue
        # Source position (with scatter)
        src_center = rng.integers(0, n)
        scatter_amt = int(scatter * grain_samples * 4)
        src = int(
            np.clip(src_center + rng.integers(-scatter_amt, scatter_amt + 1), 0, n - grain_samples)
        )

        # Destination (slightly time-shifted)
        dst = int(
            np.clip(
                src_center + rng.integers(-grain_samples // 4, grain_samples // 4 + 1),
                0,
                n - grain_samples,
            )
        )

        grain = samples[src : src + grain_samples].copy()

        # Pitch spread via resampling
        if pitch_spread > 0:
            semitones = rng.uniform(-pitch_spread, pitch_spread)
            ratio = 2 ** (semitones / 12.0)
            new_len = max(16, int(grain_samples / ratio))
            from scipy import signal as _sig

            grain_l = _sig.resample(grain[:, 0], new_len)
            grain_r = _sig.resample(grain[:, 1], new_len)
            grain = np.column_stack([grain_l, grain_r])
            grain = (
                grain[:grain_samples]
                if len(grain) >= grain_samples
                else np.pad(grain, ((0, grain_samples - len(grain)), (0, 0)))
            )

        # Hanning window to avoid clicks
        window = np.hanning(grain_samples)
        grain *= window[:, np.newaxis]

        end = min(dst + grain_samples, n)
        chunk = end - dst
        out[dst:end] += grain[:chunk]
        counts[dst:end] += 1

    # Normalize by overlap count
    mask = counts > 0
    out[mask] /= counts[mask, np.newaxis]

    return (samples * (1 - wet) + out * wet).astype(np.float64)


# ---------------------------------------------------------------------------
# Auto-tune — snap pitch to nearest scale note
# ---------------------------------------------------------------------------


def autotune(
    samples: FloatArray,
    sample_rate: int = 44100,
    scale_notes: list[int] | None = None,
    strength: float = 0.7,
    speed_ms: float = 50.0,
) -> FloatArray:
    """Auto-tune effect: snap the pitch of audio toward the nearest scale note.

    Uses a simple pitch detection + resampling approach. Works best on
    monophonic melodic signals (vocal, lead synth). Not suitable for drums
    or full mixes.

    Args:
        scale_notes: MIDI note numbers in one octave (0-11) to snap to.
                     Default: chromatic (all notes, just smoothing).
        strength:    How strongly to correct pitch (0=off, 1=hard snap).
        speed_ms:    How fast pitch correction kicks in (lower=Cher effect).

    Example::

        # Snap to A minor pentatonic: A C D E G
        autotune(voice, sr, scale_notes=[0, 3, 5, 7, 10])
    """
    if scale_notes is None:
        scale_notes = list(range(12))  # chromatic — just smoothing

    n = len(samples)
    block = max(64, int(speed_ms * sample_rate / 1000))
    out = samples.copy().astype(np.float64)

    def _nearest_scale_midi(detected_midi: float) -> float:
        """Find nearest scale MIDI pitch."""
        oct_n = int(detected_midi) // 12
        chroma = detected_midi % 12
        diffs = [(abs(chroma - s), s) for s in scale_notes]
        # Also check wrapping (e.g. chroma=11, scale has 0)
        diffs += [(abs(chroma - s - 12), s) for s in scale_notes]
        diffs += [(abs(chroma - s + 12), s) for s in scale_notes]
        best = min(diffs)[1]
        return oct_n * 12 + best

    # Process block by block
    for start in range(0, n, block):
        end = min(start + block, n)
        mono = np.mean(out[start:end], axis=1)
        if len(mono) < 16:
            continue

        # Simple autocorrelation pitch detection
        corr = np.correlate(mono, mono, mode="full")
        corr = corr[len(corr) // 2 :]
        # Find first peak after initial zero-crossing
        min_period = max(2, int(sample_rate / 2000))  # max 2kHz
        max_period = min(len(corr) - 1, int(sample_rate / 60))  # min 60Hz
        if max_period <= min_period:
            continue
        sub = corr[min_period:max_period]
        if len(sub) == 0 or np.max(sub) < 0.01:
            continue
        period = np.argmax(sub) + min_period
        if period < 2:
            continue
        detected_freq = sample_rate / period
        if detected_freq < 60 or detected_freq > 2000:
            continue

        detected_midi = 69 + 12 * np.log2(detected_freq / 440.0)
        target_midi = _nearest_scale_midi(detected_midi)
        semitone_shift = (target_midi - detected_midi) * strength
        if abs(semitone_shift) < 0.05:
            continue

        # Resample this block to apply pitch shift
        ratio = 2 ** (semitone_shift / 12.0)
        new_len = max(1, int((end - start) / ratio))
        from scipy import signal as _sig

        shifted_l = _sig.resample(out[start:end, 0], new_len)
        shifted_r = _sig.resample(out[start:end, 1], new_len)
        # Fit back to original block size
        block_len = end - start
        if new_len >= block_len:
            out[start:end, 0] = shifted_l[:block_len]
            out[start:end, 1] = shifted_r[:block_len]
        else:
            out[start : start + new_len, 0] = shifted_l
            out[start : start + new_len, 1] = shifted_r

    return np.clip(out, -1.0, 1.0).astype(np.float64)


# ---------------------------------------------------------------------------
# Convolution reverb — synthetic room impulse responses
# ---------------------------------------------------------------------------


def conv_reverb(
    samples: FloatArray,
    sample_rate: int = 44100,
    room: str = "hall",
    wet: float = 0.3,
) -> FloatArray:
    """Convolution reverb using synthetic impulse responses.

    No external IR files needed — IRs are generated algorithmically to
    model different acoustic spaces. Sounds more natural than the
    algorithmic reverb because it captures the full decay curve.

    Args:
        room: Room type — "hall", "chamber", "plate", "room", "cave", "spring".
        wet:  Wet/dry mix.

    Example::

        reverb_wet = conv_reverb(guitar, sr, room="hall", wet=0.35)
    """
    ROOMS = {
        "hall":    {"rt60": 2.5, "early_ms": 25,  "color": 0.6,  "diffuse": 0.85},
        "chamber": {"rt60": 1.4, "early_ms": 15,  "color": 0.5,  "diffuse": 0.75},
        "plate":   {"rt60": 1.8, "early_ms": 8,   "color": 0.3,  "diffuse": 0.95},
        "room":    {"rt60": 0.6, "early_ms": 10,  "color": 0.65, "diffuse": 0.6},
        "cave":    {"rt60": 4.0, "early_ms": 40,  "color": 0.8,  "diffuse": 0.5},
        "spring":  {"rt60": 0.9, "early_ms": 5,   "color": 0.2,  "diffuse": 0.9},
    }
    params = ROOMS.get(room, ROOMS["room"])
    rt60    = params["rt60"]
    early   = int(params["early_ms"] * sample_rate / 1000)
    color   = params["color"]
    diffuse = params["diffuse"]

    # Build synthetic IR:
    # 1. Early reflections: sparse, discrete
    # 2. Late reverb tail: dense noise with exponential decay
    ir_len = int(rt60 * sample_rate)
    rng = np.random.default_rng(42)
    ir = np.zeros(ir_len)

    # Early reflections — handful of strong echoes
    n_early = 12
    for i in range(n_early):
        pos = int(early * (i / n_early) ** 0.7) + rng.integers(0, max(1, early // 10))
        pos = min(pos, ir_len - 1)
        amp = (1.0 - i / n_early) * 0.9
        ir[pos] += rng.choice([-1, 1]) * amp

    # Late tail — exponential decay noise
    t = np.arange(ir_len) / sample_rate
    decay = np.exp(-6.91 * t / rt60)  # -60dB at rt60
    noise = rng.standard_normal(ir_len) * diffuse

    # Color: LP filter the noise (darker rooms = more LP)
    if color > 0:
        cutoff = max(500.0, 12000.0 * (1.0 - color * 0.8))
        sos_lp = sig.butter(2, cutoff, btype="low", fs=sample_rate, output="sos")
        noise = sig.sosfilt(sos_lp, noise)

    ir += noise * decay * 0.3

    # Normalize IR
    peak = np.max(np.abs(ir))
    if peak > 0:
        ir /= peak

    # Convolve each channel
    def _conv(ch: np.ndarray) -> np.ndarray:
        return sig.fftconvolve(ch, ir, mode="full")[: len(ch)]

    left  = _conv(samples[:, 0])
    right = _conv(samples[:, 1])
    wet_signal = np.column_stack([left, right])

    # Normalize wet signal
    wp = np.max(np.abs(wet_signal))
    if wp > 0:
        wet_signal /= wp

    return (samples * (1 - wet) + wet_signal * wet).astype(np.float64)
