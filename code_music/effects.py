"""Audio effects: reverb, delay, chorus, distortion, filters, compress, pan.

All functions take/return stereo float64 arrays shape (N, 2).
All inner loops use scipy/numpy — no Python sample-level loops.
"""

from __future__ import annotations

import math
from typing import Callable

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
# Slapback delay — single short echo (rockabilly, early rock)
# ---------------------------------------------------------------------------


def slapback(
    samples: FloatArray,
    sample_rate: int = 44100,
    delay_ms: float = 120.0,
    level: float = 0.6,
) -> FloatArray:
    """Slapback delay — a single short echo with no feedback.

    The defining effect of 1950s rockabilly, early rock, and surf guitar.
    Sam Phillips at Sun Records invented this by running tape between two
    machines. One echo, 75–175ms, no repeats. Simple and effective.

    Also useful on vocals, snare drums, and lead instruments for presence
    without the wash of a full delay or reverb.

    Args:
        delay_ms: Echo time in milliseconds (75–175ms typical for slapback).
        level:    Volume of the echo relative to dry signal (0.0–1.0).

    Example::

        slapback(vocal, sr, delay_ms=120.0, level=0.6)
        slapback(guitar, sr, delay_ms=90.0, level=0.5)
    """
    d = max(1, int(delay_ms * sample_rate / 1000))
    n = len(samples)
    if d >= n:
        return samples.copy().astype(np.float64)

    echo = np.zeros_like(samples)
    echo[d:] = samples[:-d] * level

    out = samples + echo
    peak = np.max(np.abs(out))
    if peak > 1.0:
        out /= peak
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
    ir_file: str | None = None,
) -> FloatArray:
    """Convolution reverb — synthetic rooms or load a real IR .wav file.

    Two modes:
      1. Synthetic IR (default): pass ``room="hall"`` etc. No files needed.
      2. Real IR file: pass ``ir_file="path/to/impulse.wav"``. The WAV is
         loaded, resampled to match sample_rate if needed, and used as the
         impulse response. This captures the exact acoustic signature of a
         real space — studios, churches, stairwells, plates, springs.

    Args:
        room:    Synthetic room type (ignored when ir_file is set).
                 Options: "hall", "chamber", "plate", "room", "cave", "spring".
        wet:     Wet/dry mix (0.0 = dry, 1.0 = full wet).
        ir_file: Path to a .wav impulse response file. When provided, the
                 synthetic room is ignored and this IR is used instead.

    Examples::

        # Synthetic room
        conv_reverb(guitar, sr, room="hall", wet=0.35)

        # Real IR file
        conv_reverb(guitar, sr, ir_file="irs/church.wav", wet=0.4)
    """
    # ── Load real IR file if provided ─────────────────────────────────────
    if ir_file is not None:
        import wave as _wave
        from pathlib import Path as _Path

        ir_path = _Path(ir_file)
        if not ir_path.exists():
            raise FileNotFoundError(f"IR file not found: {ir_file}")

        with _wave.open(str(ir_path), "rb") as wf:
            ir_sr = wf.getframerate()
            ir_n = wf.getnframes()
            ir_ch = wf.getnchannels()
            ir_sw = wf.getsampwidth()
            ir_raw = wf.readframes(ir_n)

        ir_dtype = np.int16 if ir_sw == 2 else np.int32
        ir_data = np.frombuffer(ir_raw, dtype=ir_dtype).astype(np.float64)
        ir_data /= 32768.0 if ir_sw == 2 else 2147483648.0

        # Mix to mono if stereo
        if ir_ch == 2:
            ir_data = ir_data.reshape(-1, 2).mean(axis=1)

        # Resample IR to match sample_rate if needed
        if ir_sr != sample_rate:
            new_len = int(len(ir_data) * sample_rate / ir_sr)
            ir_data = sig.resample(ir_data, new_len)

        # Normalize IR
        pk = np.max(np.abs(ir_data))
        if pk > 0:
            ir_data /= pk

        # Convolve
        left = sig.fftconvolve(samples[:, 0], ir_data, mode="full")[: len(samples)]
        right = sig.fftconvolve(samples[:, 1], ir_data, mode="full")[: len(samples)]
        wet_signal = np.column_stack([left, right])
        wp = np.max(np.abs(wet_signal))
        if wp > 0:
            wet_signal /= wp
        return (samples * (1 - wet) + wet_signal * wet).astype(np.float64)

    # ── Synthetic IR (no file provided) ────────────────────────────────────
    ROOMS = {
        "hall": {"rt60": 2.5, "early_ms": 25, "color": 0.6, "diffuse": 0.85},
        "chamber": {"rt60": 1.4, "early_ms": 15, "color": 0.5, "diffuse": 0.75},
        "plate": {"rt60": 1.8, "early_ms": 8, "color": 0.3, "diffuse": 0.95},
        "room": {"rt60": 0.6, "early_ms": 10, "color": 0.65, "diffuse": 0.6},
        "cave": {"rt60": 4.0, "early_ms": 40, "color": 0.8, "diffuse": 0.5},
        "spring": {"rt60": 0.9, "early_ms": 5, "color": 0.2, "diffuse": 0.9},
    }
    params = ROOMS.get(room, ROOMS["room"])
    rt60 = params["rt60"]
    early = int(params["early_ms"] * sample_rate / 1000)
    color = params["color"]
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

    left = _conv(samples[:, 0])
    right = _conv(samples[:, 1])
    wet_signal = np.column_stack([left, right])

    # Normalize wet signal
    wp = np.max(np.abs(wet_signal))
    if wp > 0:
        wet_signal /= wp

    return (samples * (1 - wet) + wet_signal * wet).astype(np.float64)


# ---------------------------------------------------------------------------
# Multi-band EQ — parametric equalizer with configurable bands
# ---------------------------------------------------------------------------


def eq(
    samples: FloatArray,
    sample_rate: int = 44100,
    bands: list[tuple[float, float, float]] | None = None,
) -> FloatArray:
    """Parametric multi-band equalizer.

    Each band is a (frequency_hz, gain_db, q) tuple:
      frequency_hz: Centre frequency of the band.
      gain_db:      Boost (+) or cut (-) in decibels. 0 = no change.
      q:            Bandwidth (higher Q = narrower). Typical: 0.5–4.0.

    Args:
        bands: List of (freq_hz, gain_db, q) tuples.
               Default: gentle presence boost and low-end warmth.

    Example::

        # Brighten highs, add warmth, cut muddy mids
        eq(guitar, sr, bands=[
            (80,   +3.0, 0.7),   # low warmth
            (500,  -2.0, 1.0),   # cut mud
            (3000, +2.5, 1.2),   # presence
            (8000, +1.5, 0.8),   # air
        ])
    """
    if bands is None:
        bands = [
            (100.0, +1.5, 0.7),  # low warmth
            (3000.0, +1.0, 1.0),  # presence
            (8000.0, +0.8, 0.8),  # air
        ]

    result = samples.copy().astype(np.float64)

    for freq_hz, gain_db, q in bands:
        if abs(gain_db) < 0.1:
            continue
        freq_hz = np.clip(freq_hz, 20.0, sample_rate / 2 - 1)
        q = max(0.1, q)

        # Peaking EQ biquad coefficients
        A = 10 ** (gain_db / 40.0)
        w0 = 2 * math.pi * freq_hz / sample_rate
        alpha = math.sin(w0) / (2 * q)

        b0 = 1 + alpha * A
        b1 = -2 * math.cos(w0)
        b2 = 1 - alpha * A
        a0 = 1 + alpha / A
        a1 = -2 * math.cos(w0)
        a2 = 1 - alpha / A

        sos = np.array([[b0 / a0, b1 / a0, b2 / a0, 1.0, a1 / a0, a2 / a0]])
        result[:, 0] = sig.sosfilt(sos, result[:, 0])
        result[:, 1] = sig.sosfilt(sos, result[:, 1])

    return np.clip(result, -1.0, 1.0).astype(np.float64)


# ---------------------------------------------------------------------------
# EffectsChain — ordered, per-step wet/dry and bypass
# ---------------------------------------------------------------------------


class _Step:
    """One link in an EffectsChain."""

    __slots__ = ("fn", "wet", "bypass", "label", "kwargs")

    def __init__(
        self,
        fn: Callable[[FloatArray, int], FloatArray],
        wet: float = 1.0,
        bypass: bool = False,
        label: str = "",
        kwargs: dict | None = None,
    ) -> None:
        self.fn = fn
        self.wet = max(0.0, min(wet, 1.0))
        self.bypass = bypass
        self.label = label or getattr(fn, "__name__", "effect")
        self.kwargs = kwargs or {}

    def __repr__(self) -> str:
        state = "bypass" if self.bypass else f"wet={self.wet:.2f}"
        return f"Step({self.label!r}, {state})"


class EffectsChain:
    """Ordered chain of audio effects with per-step wet/dry and bypass.

    Replaces the old ``song._effects = { name: lambda }`` pattern with
    a composable, inspectable object.

    Example::

        from code_music.effects import EffectsChain, reverb, delay, compress

        chain = (
            EffectsChain()
            .add(reverb, room_size=0.7, wet=0.3)
            .add(delay, delay_ms=375, feedback=0.3, wet=0.25)
            .add(compress, threshold=0.6, ratio=4.0)
        )

        # Apply to a track
        song.effects["pad"] = chain

        # Or call directly
        processed = chain(samples, sample_rate)
    """

    def __init__(self) -> None:
        self._steps: list[_Step] = []

    # -- Building ----------------------------------------------------------

    def add(
        self,
        effect_fn: Callable,
        *,
        wet: float = 1.0,
        bypass: bool = False,
        label: str = "",
        **kwargs,
    ) -> "EffectsChain":
        """Append an effect to the chain.

        Args:
            effect_fn: Any code-music effect function (e.g. ``reverb``).
            wet:       Dry/wet mix for this step (0.0 = fully dry, 1.0 = fully wet).
            bypass:    If True, this step is skipped during processing.
            label:     Optional human-readable name for this step.
            **kwargs:  Extra keyword arguments forwarded to *effect_fn*.

        Returns:
            self, for chaining.
        """
        if kwargs:
            bound_fn = lambda s, sr, _fn=effect_fn, _kw=kwargs: _fn(s, sr, **_kw)  # noqa: E731
            bound_fn.__name__ = label or getattr(effect_fn, "__name__", "effect")
        else:
            bound_fn = effect_fn

        self._steps.append(_Step(bound_fn, wet=wet, bypass=bypass, label=label, kwargs=kwargs))
        return self

    def remove(self, index: int) -> "EffectsChain":
        """Remove the step at *index*."""
        del self._steps[index]
        return self

    def set_bypass(self, index: int, bypass: bool = True) -> "EffectsChain":
        """Enable or disable bypass on the step at *index*."""
        self._steps[index].bypass = bypass
        return self

    def set_wet(self, index: int, wet: float) -> "EffectsChain":
        """Set wet/dry mix on the step at *index*."""
        self._steps[index].wet = max(0.0, min(wet, 1.0))
        return self

    # -- Processing --------------------------------------------------------

    def __call__(self, samples: FloatArray, sample_rate: int) -> FloatArray:
        """Run *samples* through the chain in order."""
        result = samples
        for step in self._steps:
            if step.bypass:
                continue
            processed = step.fn(result, sample_rate)
            if step.wet >= 1.0:
                result = processed
            elif step.wet <= 0.0:
                continue
            else:
                result = result * (1.0 - step.wet) + processed * step.wet
        return result

    # -- Introspection -----------------------------------------------------

    def __len__(self) -> int:
        return len(self._steps)

    def __repr__(self) -> str:
        steps = ", ".join(repr(s) for s in self._steps)
        return f"EffectsChain([{steps}])"

    def __iter__(self):
        return iter(self._steps)

    @property
    def steps(self) -> list[_Step]:
        """Read-only view of the chain's steps."""
        return list(self._steps)

    # -- Serialization -----------------------------------------------------

    def to_dict(self) -> list[dict]:
        """Serialize the chain to a list of plain dicts.

        Each step becomes ``{"effect": "<name>", "wet": float, "bypass": bool, **kwargs}``.
        Only works for steps added via ``add(effect_fn, **kwargs)`` where kwargs
        were captured. Bare lambdas or pre-bound callables serialize with just
        the label and wet/bypass (no kwargs).

        Example::

            data = chain.to_dict()
            # [{"effect": "reverb", "wet": 0.3, "bypass": false, "room_size": 0.7}]
        """
        result = []
        for step in self._steps:
            entry: dict = {
                "effect": step.label,
                "wet": step.wet,
                "bypass": step.bypass,
            }
            entry.update(step.kwargs)
            result.append(entry)
        return result

    @classmethod
    def from_dict(cls, data: list[dict]) -> "EffectsChain":
        """Reconstruct an EffectsChain from serialized dicts.

        Looks up effect functions by name from this module's public API.

        Example::

            chain = EffectsChain.from_dict([
                {"effect": "reverb", "wet": 0.3, "room_size": 0.7},
                {"effect": "delay", "wet": 0.2, "delay_ms": 375},
            ])
        """
        import sys

        module = sys.modules[__name__]
        chain = cls()
        for entry in data:
            name = entry["effect"]
            wet = entry.get("wet", 1.0)
            bypass = entry.get("bypass", False)
            kwargs = {k: v for k, v in entry.items() if k not in ("effect", "wet", "bypass")}

            fn = getattr(module, name, None)
            if fn is None or not callable(fn):
                raise ValueError(f"Unknown effect function: {name!r}")

            chain.add(fn, wet=wet, bypass=bypass, label=name, **kwargs)
        return chain


# ---------------------------------------------------------------------------
# Time-stretch and pitch-shift (v141.0)
# ---------------------------------------------------------------------------


def time_stretch(
    samples: FloatArray,
    sample_rate: int = 44100,
    rate: float = 1.0,
    grain_size_ms: float = 40.0,
) -> FloatArray:
    """Time-stretch audio without changing pitch.

    Grain-based overlap-add (OLA) stretcher. Rate > 1.0 speeds up (shorter),
    rate < 1.0 slows down (longer). Pitch stays the same.

    Args:
        samples:       Mono or stereo audio.
        sample_rate:   Sample rate (used for grain size calculation).
        rate:          Stretch factor. 0.5 = half speed (2x longer),
                       2.0 = double speed (half length).
        grain_size_ms: Grain window size in milliseconds.

    Returns:
        Time-stretched audio (same sample rate, different length).

    Example::

        >>> import numpy as np
        >>> audio = np.random.randn(44100, 2) * 0.1
        >>> slow = time_stretch(audio, 44100, rate=0.5)
        >>> slow.shape[0] > audio.shape[0]
        True
    """
    if rate <= 0:
        raise ValueError("rate must be positive")
    if abs(rate - 1.0) < 0.001:
        return samples.copy()

    is_stereo = samples.ndim == 2
    if is_stereo:
        left = _time_stretch_mono(samples[:, 0], sample_rate, rate, grain_size_ms)
        right = _time_stretch_mono(samples[:, 1], sample_rate, rate, grain_size_ms)
        min_len = min(len(left), len(right))
        return np.column_stack([left[:min_len], right[:min_len]])
    return _time_stretch_mono(samples, sample_rate, rate, grain_size_ms)


def _time_stretch_mono(mono: np.ndarray, sr: int, rate: float, grain_size_ms: float) -> np.ndarray:
    """OLA time-stretch for mono audio."""
    grain_len = max(64, int(grain_size_ms * sr / 1000))
    hop_in = grain_len // 2  # input hop
    hop_out = int(hop_in / rate)  # output hop

    # Hann window for smooth overlap
    window = np.hanning(grain_len).astype(np.float64)

    n = len(mono)
    out_len = int(n / rate) + grain_len
    out = np.zeros(out_len, dtype=np.float64)
    norm = np.zeros(out_len, dtype=np.float64)

    pos_in = 0
    pos_out = 0

    while pos_in + grain_len <= n and pos_out + grain_len <= out_len:
        grain = mono[pos_in : pos_in + grain_len] * window
        out[pos_out : pos_out + grain_len] += grain
        norm[pos_out : pos_out + grain_len] += window
        pos_in += hop_in
        pos_out += hop_out

    # Normalize overlap regions
    mask = norm > 1e-8
    out[mask] /= norm[mask]

    # Trim trailing silence
    last_nonzero = np.max(np.nonzero(np.abs(out) > 1e-10), initial=0)
    return out[: last_nonzero + 1] if last_nonzero > 0 else out


def pitch_shift(
    samples: FloatArray,
    sample_rate: int = 44100,
    semitones: float = 0.0,
    grain_size_ms: float = 40.0,
) -> FloatArray:
    """Pitch-shift audio without changing duration.

    Combines time-stretching with resampling. Shift up = positive semitones,
    shift down = negative. Duration stays the same.

    Args:
        samples:       Mono or stereo audio.
        sample_rate:   Sample rate.
        semitones:     Pitch shift in semitones. +12 = one octave up.
        grain_size_ms: Grain window size.

    Returns:
        Pitch-shifted audio (same length and sample rate).

    Example::

        >>> import numpy as np
        >>> audio = np.random.randn(44100, 2) * 0.1
        >>> shifted = pitch_shift(audio, 44100, semitones=7)
        >>> abs(shifted.shape[0] - audio.shape[0]) < 100
        True
    """
    if abs(semitones) < 0.01:
        return samples.copy()

    # Pitch shift = time-stretch by inverse ratio, then resample
    ratio = 2.0 ** (semitones / 12.0)

    # Step 1: Time-stretch to compensate for upcoming resample
    stretched = time_stretch(samples, sample_rate, rate=ratio, grain_size_ms=grain_size_ms)

    # Step 2: Resample to shift pitch (changes length back to original)
    original_len = len(samples)
    is_stereo = stretched.ndim == 2

    if is_stereo:
        left = np.interp(
            np.linspace(0, len(stretched) - 1, original_len),
            np.arange(len(stretched)),
            stretched[:, 0],
        )
        right = np.interp(
            np.linspace(0, len(stretched) - 1, original_len),
            np.arange(len(stretched)),
            stretched[:, 1],
        )
        return np.column_stack([left, right])

    return np.interp(
        np.linspace(0, len(stretched) - 1, original_len),
        np.arange(len(stretched)),
        stretched,
    )


# ---------------------------------------------------------------------------
# Cross-synthesis (v142.0)
# ---------------------------------------------------------------------------


def cross_synthesis(
    source: FloatArray,
    target: FloatArray,
    sample_rate: int = 44100,
    fft_size: int = 2048,
    blend: float = 1.0,
    wet: float = 0.9,
) -> FloatArray:
    """Cross-synthesis: apply the spectral envelope of one sound to another.

    Takes the magnitude spectrum from `target` and the phase spectrum from
    `source`. The result has the pitch/timing of `source` but the timbral
    character of `target`. Classic use: give a piano the spectrum of a voice,
    or make strings sound like a choir.

    Unlike the vocoder (which uses band-pass filters), this operates directly
    in the frequency domain via STFT for higher fidelity.

    Args:
        source:      Signal providing phase (pitch, timing).
        target:      Signal providing magnitude (timbre, spectral shape).
        sample_rate: Sample rate.
        fft_size:    FFT window size. Larger = smoother, more latency.
        blend:       How much of target's spectrum to use (0=source, 1=target).
        wet:         Wet/dry mix.

    Returns:
        Cross-synthesized audio (same shape as source).

    Example::

        >>> import numpy as np
        >>> src = np.random.randn(22050, 2) * 0.1
        >>> tgt = np.random.randn(22050, 2) * 0.1
        >>> out = cross_synthesis(src, tgt, 22050)
        >>> out.shape == src.shape
        True
    """
    n = min(len(source), len(target))
    source = source[:n]
    target = target[:n]

    is_stereo = source.ndim == 2
    if is_stereo:
        left = _cross_synth_mono(source[:, 0], target[:, 0], fft_size, blend)
        right = _cross_synth_mono(source[:, 1], target[:, 1], fft_size, blend)
        result = np.column_stack([left[:n], right[:n]])
    else:
        result = _cross_synth_mono(source, target, fft_size, blend)[:n]

    if wet < 1.0:
        result = wet * result + (1.0 - wet) * source
    return result


def _cross_synth_mono(
    source: np.ndarray, target: np.ndarray, fft_size: int, blend: float
) -> np.ndarray:
    """STFT-based cross-synthesis for mono signals."""
    hop = fft_size // 4
    window = np.hanning(fft_size).astype(np.float64)
    n = len(source)

    # Pad to multiple of hop
    pad_len = (fft_size + (n // hop) * hop) - n + fft_size
    src_pad = np.pad(source, (0, max(0, pad_len)))
    tgt_pad = np.pad(target, (0, max(0, pad_len)))

    out = np.zeros(len(src_pad), dtype=np.float64)
    norm = np.zeros(len(src_pad), dtype=np.float64)

    pos = 0
    while pos + fft_size <= len(src_pad):
        src_frame = src_pad[pos : pos + fft_size] * window
        tgt_frame = tgt_pad[pos : pos + fft_size] * window

        src_fft = np.fft.rfft(src_frame)
        tgt_fft = np.fft.rfft(tgt_frame)

        # Magnitude from target, phase from source
        src_mag = np.abs(src_fft)
        tgt_mag = np.abs(tgt_fft)
        src_phase = np.angle(src_fft)

        # Blend magnitudes
        blended_mag = (1.0 - blend) * src_mag + blend * tgt_mag

        # Reconstruct with source phase
        synth_fft = blended_mag * np.exp(1j * src_phase)
        frame = np.fft.irfft(synth_fft, n=fft_size) * window

        out[pos : pos + fft_size] += frame
        norm[pos : pos + fft_size] += window**2
        pos += hop

    # Normalize overlap
    mask = norm > 1e-8
    out[mask] /= norm[mask]
    return out[:n]


# ---------------------------------------------------------------------------
# Spatial Audio / Binaural Panner (v151.0)
# ---------------------------------------------------------------------------


def spatial_pan(
    samples: FloatArray,
    sample_rate: int = 44100,
    azimuth: float = 0.0,
    elevation: float = 0.0,
    distance: float = 1.0,
) -> FloatArray:
    """Position a mono or stereo signal in 3D space using binaural cues.

    Uses interaural time difference (ITD), interaural level difference (ILD),
    and distance attenuation to create a convincing spatial impression on
    headphones. No HRTF dataset needed - pure physics model.

    Azimuth 0 = center, +90 = hard right, -90 = hard left, 180 = behind.
    Elevation 0 = ear level, +90 = above, -90 = below.
    Distance 1.0 = close, higher = farther (attenuated + more reverb).

    Args:
        samples:     Mono (N,) or stereo (N,2) audio.
        sample_rate: Sample rate in Hz.
        azimuth:     Horizontal angle in degrees (-180 to 180).
        elevation:   Vertical angle in degrees (-90 to 90).
        distance:    Distance from listener (1.0 = nominal).

    Returns:
        Stereo (N,2) binaural audio.

    Example::

        >>> import numpy as np
        >>> mono = np.random.randn(22050) * 0.1
        >>> binaural = spatial_pan(mono, 22050, azimuth=45)
        >>> binaural.shape
        (22050, 2)
    """
    # Convert to mono if stereo
    if samples.ndim == 2:
        mono = np.mean(samples, axis=1)
    else:
        mono = samples.copy()

    n = len(mono)
    az_rad = math.radians(azimuth)
    el_rad = math.radians(elevation)

    # Head radius in meters (average human)
    head_radius = 0.0875  # ~8.75 cm

    # Speed of sound in m/s
    speed_of_sound = 343.0

    # --- Interaural Time Difference (ITD) ---
    # Woodworth formula: ITD = (r/c) * (sin(theta) + theta)
    # where theta is the azimuth angle
    itd = (head_radius / speed_of_sound) * (math.sin(abs(az_rad)) + abs(az_rad))
    itd_samples = int(itd * sample_rate)

    # --- Interaural Level Difference (ILD) ---
    # Higher frequencies are shadowed more by the head
    # Simple model: 0-6 dB based on azimuth
    ild_db = 6.0 * math.sin(abs(az_rad))
    # Elevation reduces the horizontal effect slightly
    ild_db *= math.cos(el_rad) * 0.8 + 0.2
    ild_factor = 10.0 ** (-ild_db / 20.0)

    # --- Distance attenuation ---
    # Inverse distance law: amplitude falls off as 1/distance
    dist_gain = 1.0 / max(distance, 0.1)
    # At close range, increase bass (proximity effect)
    # At far range, roll off highs (air absorption)

    # --- Build stereo output ---
    left = np.zeros(n, dtype=np.float64)
    right = np.zeros(n, dtype=np.float64)

    if azimuth >= 0:
        # Source is to the right
        # Right ear: closer, louder, no delay
        right[:] = mono * dist_gain
        # Left ear: farther, quieter, delayed
        if itd_samples > 0 and itd_samples < n:
            left[itd_samples:] = mono[:-itd_samples] * ild_factor * dist_gain
        else:
            left[:] = mono * ild_factor * dist_gain
    else:
        # Source is to the left
        left[:] = mono * dist_gain
        if itd_samples > 0 and itd_samples < n:
            right[itd_samples:] = mono[:-itd_samples] * ild_factor * dist_gain
        else:
            right[:] = mono * ild_factor * dist_gain

    # Elevation cue: slight high-frequency roll-off for sources above/below
    if abs(elevation) > 15:
        el_factor = 1.0 - min(abs(elevation) / 90.0, 1.0) * 0.3
        # Simple low-pass approximation via moving average
        kernel_size = max(2, int(abs(elevation) / 10))
        kernel = np.ones(kernel_size) / kernel_size
        left = np.convolve(left, kernel, mode="same") * el_factor + left * (1 - el_factor)
        right = np.convolve(right, kernel, mode="same") * el_factor + right * (1 - el_factor)

    return np.column_stack([left, right])


def orbit(
    samples: FloatArray,
    sample_rate: int = 44100,
    rate: float = 0.5,
    radius: float = 2.0,
    elevation: float = 0.0,
) -> FloatArray:
    """Make a sound orbit around the listener's head.

    Applies spatial_pan with a continuously rotating azimuth. The sound
    traces a circle at the given rate and radius. Classic spatial effect
    for pads, drones, and ambient textures.

    Args:
        samples:     Mono or stereo audio.
        sample_rate: Sample rate.
        rate:        Orbits per second (Hz). 0.5 = one full circle every 2s.
        radius:      Distance from listener.
        elevation:   Vertical angle (fixed during orbit).

    Returns:
        Stereo binaural audio with orbiting spatial position.

    Example::

        >>> import numpy as np
        >>> mono = np.random.randn(44100) * 0.1
        >>> orbiting = orbit(mono, 44100, rate=0.25, radius=2.0)
        >>> orbiting.shape[1]
        2
    """
    if samples.ndim == 2:
        mono = np.mean(samples, axis=1)
    else:
        mono = samples.copy()

    n = len(mono)
    # Process in chunks to smoothly animate the azimuth
    chunk_size = max(256, sample_rate // 20)  # ~50ms chunks
    out = np.zeros((n, 2), dtype=np.float64)

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        chunk = mono[start:end]

        # Calculate azimuth at the midpoint of this chunk
        t = (start + (end - start) // 2) / sample_rate
        azimuth = math.degrees(2.0 * math.pi * rate * t) % 360
        # Map 0-360 to -180..180
        if azimuth > 180:
            azimuth -= 360

        panned = spatial_pan(
            chunk, sample_rate, azimuth=azimuth, elevation=elevation, distance=radius
        )
        out[start:end] = panned

    return out


# ---------------------------------------------------------------------------
# First-Order Ambisonics (v152.0)
# ---------------------------------------------------------------------------


def encode_bformat(
    mono: FloatArray,
    azimuth: float = 0.0,
    elevation: float = 0.0,
    distance: float = 1.0,
) -> FloatArray:
    """Encode a mono signal into first-order Ambisonics B-format.

    B-format uses 4 channels (W, X, Y, Z) to represent a complete 3D
    sound field. W is the omnidirectional (pressure) component. X, Y, Z
    are the figure-of-eight (velocity) components along the three axes.

    This is the standard interchange format for spatial audio. Encode
    each source separately, sum the B-format signals, then decode to
    any speaker layout or binaural.

    Args:
        mono:      Mono audio signal (N,).
        azimuth:   Horizontal angle in degrees (-180..180). 0 = front.
        elevation: Vertical angle in degrees (-90..90). 0 = ear level.
        distance:  Source distance (1.0 = nominal, >1 = farther).

    Returns:
        B-format array (N, 4) with channels [W, X, Y, Z].

    Example::

        >>> import numpy as np
        >>> mono = np.random.randn(22050) * 0.1
        >>> bformat = encode_bformat(mono, azimuth=45, elevation=0)
        >>> bformat.shape
        (22050, 4)
    """
    if mono.ndim == 2:
        mono = np.mean(mono, axis=1)

    az = math.radians(azimuth)
    el = math.radians(elevation)
    dist_gain = 1.0 / max(distance, 0.1)

    scaled = mono * dist_gain

    # First-order spherical harmonics (SN3D normalization)
    w = scaled * (1.0 / math.sqrt(2.0))  # omnidirectional
    x = scaled * math.cos(az) * math.cos(el)  # front-back
    y = scaled * math.sin(az) * math.cos(el)  # left-right
    z = scaled * math.sin(el)  # up-down

    return np.column_stack([w, x, y, z])


def sum_bformat(*signals: FloatArray) -> FloatArray:
    """Sum multiple B-format signals into a combined sound field.

    All inputs must be (N, 4) B-format arrays of the same length.
    The result is a single B-format representing all sources together.

    Args:
        *signals: B-format arrays to sum.

    Returns:
        Combined B-format (N, 4).
    """
    if not signals:
        raise ValueError("Need at least one B-format signal")

    n = min(s.shape[0] for s in signals)
    result = np.zeros((n, 4), dtype=np.float64)
    for s in signals:
        result += s[:n]
    return result


def decode_bformat(
    bformat: FloatArray,
    layout: str = "binaural",
    sample_rate: int = 44100,
) -> FloatArray:
    """Decode B-format to a specific speaker layout or binaural.

    Supported layouts:
        'binaural': 2-channel headphone output (virtual speakers at +/-30)
        'stereo':   2-channel standard stereo (L/R at +/-30)
        'quad':     4-channel quadraphonic (FL, FR, RL, RR)
        '5.1':      6-channel surround (L, R, C, LFE, LS, RS)

    Args:
        bformat:     B-format array (N, 4) with [W, X, Y, Z].
        layout:      Target speaker layout.
        sample_rate: Sample rate (used for binaural ITD).

    Returns:
        Multi-channel audio. Shape depends on layout:
        binaural/stereo: (N, 2), quad: (N, 4), 5.1: (N, 6).

    Example::

        >>> import numpy as np
        >>> bf = np.random.randn(22050, 4) * 0.1
        >>> stereo = decode_bformat(bf, "stereo")
        >>> stereo.shape
        (22050, 2)
    """
    w, x, y = bformat[:, 0], bformat[:, 1], bformat[:, 2]
    # z = bformat[:, 3]  # reserved for height decoding in higher-order systems

    if layout == "stereo":
        # Virtual speakers at +/-30 degrees
        az_l = math.radians(30)
        az_r = math.radians(-30)
        left = w / math.sqrt(2) + x * math.cos(az_l) + y * math.sin(az_l)
        right = w / math.sqrt(2) + x * math.cos(az_r) + y * math.sin(az_r)
        return np.column_stack([left, right])

    if layout == "binaural":
        # Decode to stereo first, then apply subtle ITD for headphones
        stereo = decode_bformat(bformat, "stereo", sample_rate)
        # Add cross-feed for more natural headphone listening
        cross = 0.15
        left = stereo[:, 0] + cross * stereo[:, 1]
        right = stereo[:, 1] + cross * stereo[:, 0]
        return np.column_stack([left, right])

    if layout == "quad":
        # 4 speakers: FL(+45), FR(-45), RL(+135), RR(-135)
        angles = [45, -45, 135, -135]
        channels = []
        for az_deg in angles:
            az = math.radians(az_deg)
            ch = w / math.sqrt(2) + x * math.cos(az) + y * math.sin(az)
            channels.append(ch)
        return np.column_stack(channels)

    if layout == "5.1":
        # L(+30), R(-30), C(0), LFE(omni low), LS(+110), RS(-110)
        angles = [30, -30, 0, 0, 110, -110]
        channels = []
        for i, az_deg in enumerate(angles):
            az = math.radians(az_deg)
            ch = w / math.sqrt(2) + x * math.cos(az) + y * math.sin(az)
            if i == 3:  # LFE: just the omnidirectional low end
                ch = w * 0.5
            channels.append(ch)
        return np.column_stack(channels)

    raise ValueError(f"Unknown layout: {layout!r}. Use binaural/stereo/quad/5.1")


def doppler(
    samples: FloatArray,
    sample_rate: int = 44100,
    speed: float = 10.0,
    direction: str = "pass_by",
    closest_distance: float = 2.0,
) -> FloatArray:
    """Apply Doppler pitch shift to simulate a moving sound source.

    Models the frequency shift caused by relative motion between source
    and listener. An approaching source is pitched up, a receding source
    is pitched down. The classic ambulance siren effect.

    Args:
        samples:           Mono or stereo audio.
        sample_rate:       Sample rate.
        speed:             Source speed in m/s (10 = walking, 30 = car, 340 = Mach 1).
        direction:         Movement pattern:
                           'pass_by' - approaches then recedes (full flyby)
                           'approaching' - constant approach (pitch up)
                           'receding' - constant recession (pitch down)
        closest_distance:  Minimum distance at closest point (meters).

    Returns:
        Doppler-shifted audio (same shape as input).

    Example::

        >>> import numpy as np
        >>> tone = np.sin(np.linspace(0, 440*2*np.pi, 22050)) * 0.3
        >>> shifted = doppler(tone, 22050, speed=30, direction="pass_by")
        >>> shifted.shape == tone.shape
        True
    """
    speed_of_sound = 343.0  # m/s

    if samples.ndim == 2:
        mono = np.mean(samples, axis=1)
    else:
        mono = samples.copy()

    n = len(mono)
    t = np.arange(n) / sample_rate

    # Calculate source position over time
    if direction == "pass_by":
        # Source moves from far left to far right, closest at midpoint
        total_time = n / sample_rate
        # Position along the travel axis (meters)
        x_pos = speed * (t - total_time / 2)
        # Distance from listener (Pythagorean)
        distance = np.sqrt(x_pos**2 + closest_distance**2)
        # Radial velocity (rate of change of distance)
        radial_velocity = speed * x_pos / distance
    elif direction == "approaching":
        # Constant approach from far away
        start_dist = speed * (n / sample_rate) + closest_distance
        distance = start_dist - speed * t
        distance = np.maximum(distance, closest_distance)
        radial_velocity = np.full(n, -speed)
    elif direction == "receding":
        distance = closest_distance + speed * t
        radial_velocity = np.full(n, speed)
    else:
        return mono if samples.ndim == 1 else samples.copy()

    # Doppler ratio: f_observed = f_source * c / (c + v_radial)
    doppler_ratio = speed_of_sound / (speed_of_sound + radial_velocity)

    # Distance attenuation
    dist_gain = closest_distance / np.maximum(distance, 0.1)

    # Apply pitch shift via variable-rate resampling
    # Build a time-warped read position
    phase = np.cumsum(doppler_ratio) / sample_rate * sample_rate
    # Interpolate the source at the warped positions
    indices = np.clip(phase, 0, n - 1)
    i0 = np.floor(indices).astype(np.intp)
    i1 = np.minimum(i0 + 1, n - 1)
    frac = indices - i0
    resampled = mono[i0] * (1.0 - frac) + mono[i1] * frac

    # Apply distance attenuation
    result = resampled * dist_gain

    if samples.ndim == 2:
        return np.column_stack([result, result])
    return result


def spatial_mix(
    song,
    sample_rate: int = 44100,
    layout: str = "binaural",
) -> FloatArray:
    """Render a Song with spatial positioning applied to all tracks.

    Tracks with spatial_azimuth set are encoded to B-format at their
    position, summed into a combined sound field, then decoded to the
    target layout. Tracks without spatial attributes use standard
    stereo panning.

    Args:
        song:        Song object.
        sample_rate: Sample rate.
        layout:      Output layout: 'binaural', 'stereo', 'quad', '5.1'.

    Returns:
        Multi-channel audio array.

    Example::

        >>> from code_music import Song, Track, Note
        >>> song = Song(title="3D", bpm=120, sample_rate=22050)
        >>> tr = song.add_track(Track(spatial_azimuth=45))
        >>> tr.add(Note("C", 4, 2.0))
        >>> audio = spatial_mix(song, 22050)
        >>> audio.shape[1]
        2
    """
    from .synth import Synth

    synth = Synth(sample_rate=sample_rate)
    total_beats = song.total_beats

    # Render each track to mono, encode to B-format
    bformat_signals: list[FloatArray] = []
    stereo_signals: list[FloatArray] = []
    max_len = 0

    for track in song.tracks:
        mono = synth.render_track(track, song.bpm, total_beats)
        max_len = max(max_len, len(mono))

        if track.spatial_azimuth is not None:
            # Spatial track: encode to B-format
            if track.spatial_orbit_rate is not None:
                # Orbit: encode in chunks with rotating azimuth
                chunk_size = max(256, sample_rate // 20)
                bf = np.zeros((len(mono), 4), dtype=np.float64)
                for start in range(0, len(mono), chunk_size):
                    end = min(start + chunk_size, len(mono))
                    t = (start + (end - start) // 2) / sample_rate
                    az = (track.spatial_azimuth + 360 * track.spatial_orbit_rate * t) % 360
                    if az > 180:
                        az -= 360
                    chunk_bf = encode_bformat(
                        mono[start:end],
                        azimuth=az,
                        elevation=track.spatial_elevation,
                        distance=track.spatial_distance,
                    )
                    bf[start:end] = chunk_bf
                bformat_signals.append(bf)
            else:
                bf = encode_bformat(
                    mono,
                    azimuth=track.spatial_azimuth,
                    elevation=track.spatial_elevation,
                    distance=track.spatial_distance,
                )
                bformat_signals.append(bf)
        else:
            # Standard stereo pan
            angle = (track.pan + 1) / 2 * math.pi / 2
            stereo = np.zeros((len(mono), 2), dtype=np.float64)
            stereo[:, 0] = mono * math.cos(angle) * track.volume
            stereo[:, 1] = mono * math.sin(angle) * track.volume
            stereo_signals.append(stereo)

    # Determine output channel count
    if layout == "quad":
        out_channels = 4
    elif layout == "5.1":
        out_channels = 6
    else:
        out_channels = 2

    result = np.zeros((max_len, out_channels), dtype=np.float64)

    # Sum and decode B-format signals
    if bformat_signals:
        # Pad all to max_len
        padded = []
        for bf in bformat_signals:
            if len(bf) < max_len:
                bf = np.pad(bf, ((0, max_len - len(bf)), (0, 0)))
            padded.append(bf[:max_len])
        combined_bf = sum_bformat(*padded)
        decoded = decode_bformat(combined_bf, layout, sample_rate)
        result[: len(decoded)] += decoded[:max_len]

    # Add standard stereo signals
    for stereo in stereo_signals:
        slen = min(len(stereo), max_len)
        if out_channels == 2:
            result[:slen] += stereo[:slen]
        else:
            # Map stereo to front L/R channels
            result[:slen, 0] += stereo[:slen, 0]
            result[:slen, 1] += stereo[:slen, 1]

    # Normalize
    peak = np.max(np.abs(result))
    if peak > 0:
        result = np.tanh(result / peak * 0.95)

    return result
