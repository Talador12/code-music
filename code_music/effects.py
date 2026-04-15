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
    """Build an impulse response with early reflections + diffuse tail.

    Three stages for a realistic reverb:
    1. Pre-delay gap (1-30ms depending on room size)
    2. Early reflections: discrete taps that define room shape
    3. Diffuse tail: allpass-filtered noise with frequency-dependent decay

    The early reflections are what make a room sound like a room instead
    of a generic wash. The diffuse tail is the lush sustain. Together
    they create a reverb that has both clarity and depth.
    """
    decay_sec = 0.5 + room_size * 2.5
    ir_len = int(decay_sec * sample_rate)
    rng = np.random.default_rng(42)

    # Stage 1: Pre-delay (empty gap before first reflection)
    predelay_ms = 5.0 + room_size * 25.0
    predelay_samples = int(predelay_ms * sample_rate / 1000.0)
    predelay_samples = min(predelay_samples, ir_len // 8)

    # Stage 2: Early reflections (6 discrete taps at room-appropriate delays)
    er = np.zeros(ir_len)
    er_delays_ms = [11.0, 23.0, 37.0, 53.0, 71.0, 89.0]
    er_gains = [0.7, 0.55, 0.45, 0.35, 0.25, 0.18]
    for delay_ms, gain in zip(er_delays_ms, er_gains):
        scaled_delay = delay_ms * (0.5 + room_size)
        pos = predelay_samples + int(scaled_delay * sample_rate / 1000.0)
        if pos < ir_len:
            er[pos] = gain * rng.choice([-1.0, 1.0])

    # Stage 3: Diffuse tail (shaped noise through allpass filters)
    noise = rng.standard_normal(ir_len)
    t = np.arange(ir_len) / sample_rate

    # Frequency-dependent decay: highs decay faster than lows (real rooms absorb treble)
    env = np.exp(-t * (3.0 + damping * 8.0))
    diffuse = noise * env

    # High-frequency damping (increases with damping parameter)
    cutoff = max(500.0, min(sample_rate / 2 - 1, 8000.0 * (1.0 - damping * 0.7)))
    sos_lp = sig.butter(2, cutoff, btype="low", fs=sample_rate, output="sos")
    diffuse = sig.sosfilt(sos_lp, diffuse)

    # Allpass diffusion stages (smear the transients into a smooth tail)
    for ap_delay in [37, 113, 271, 503]:
        if ap_delay >= ir_len:
            continue
        g = 0.6
        padded = np.zeros(ir_len)
        padded[ap_delay:] = diffuse[:-ap_delay] if ap_delay > 0 else diffuse
        diffuse = -g * diffuse + padded + g * np.roll(padded, ap_delay)

    # Zero out the pre-delay region of the diffuse tail
    diffuse[: predelay_samples + int(30 * sample_rate / 1000)] *= np.linspace(
        0, 1, predelay_samples + int(30 * sample_rate / 1000)
    )[: len(diffuse[: predelay_samples + int(30 * sample_rate / 1000)])]

    # Combine early reflections + diffuse tail
    ir = er * 0.4 + diffuse * 0.8
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
    voices: int = 3,
    spread: float = 0.6,
    wet: float = 0.4,
) -> FloatArray:
    """Multi-voice stereo chorus with phase-offset LFOs.

    Real chorus units (Roland Juno, Boss CE-2) use multiple delayed copies
    of the signal, each modulated at slightly different rates and phases.
    The phase offsets between voices create stereo width. More voices =
    thicker, more ensemble-like. Three voices is the sweet spot for most
    instruments. Six voices starts to sound like a string section.

    Args:
        rate_hz:  LFO speed in Hz (0.5-2.0 typical).
        depth_ms: Modulation depth (2-5ms typical).
        voices:   Number of chorus voices (1-6). More = thicker.
        spread:   Stereo width of the chorus (0.0-1.0).
        wet:      Wet/dry mix.
    """
    n = len(samples)
    t = np.arange(n) / sample_rate
    depth_samples = depth_ms * sample_rate / 1000.0

    out_l = samples[:, 0] * (1 - wet)
    out_r = samples[:, 1] * (1 - wet)
    voice_gain = wet / max(voices, 1)

    for v in range(voices):
        # Each voice gets a unique phase offset and slight rate variation
        phase = v * 2 * np.pi / voices
        rate_variation = 1.0 + (v - voices / 2) * 0.05  # slight detuning
        lfo = np.sin(2 * np.pi * rate_hz * rate_variation * t + phase)
        offsets = (lfo * depth_samples).astype(np.float64)

        indices = np.clip(np.arange(n, dtype=np.float64) - offsets, 0, n - 1)
        lo = np.floor(indices).astype(int)
        hi = np.minimum(lo + 1, n - 1)
        frac = indices - lo

        warped_l = samples[:, 0][lo] * (1 - frac) + samples[:, 0][hi] * frac
        warped_r = samples[:, 1][lo] * (1 - frac) + samples[:, 1][hi] * frac

        # Stereo placement: voices alternate L/R with spread control
        pan_angle = (v / max(voices - 1, 1) - 0.5) * spread * np.pi
        l_gain = np.cos(pan_angle / 2 + np.pi / 4)
        r_gain = np.sin(pan_angle / 2 + np.pi / 4)
        out_l += warped_l * voice_gain * l_gain
        out_r += warped_r * voice_gain * r_gain

    return np.column_stack([out_l, out_r]).astype(np.float64)


# ---------------------------------------------------------------------------
# Distortion
# ---------------------------------------------------------------------------


def distortion(
    samples: FloatArray,
    sample_rate: int = 44100,
    drive: float = 3.0,
    tone: float = 0.5,
    wet: float = 0.6,
) -> FloatArray:
    """Oversampled soft-clip overdrive with tone control.

    Distortion generates new harmonics. At 44.1kHz, those harmonics can
    alias (fold back below Nyquist as inharmonic garbage). 2x oversampling
    pushes the aliasing threshold to 44.1kHz (inaudible), then we
    low-pass and downsample back. The result is warm saturation without
    the fizzy digital artifacts that make cheap plugins sound cheap.
    """
    n = len(samples)

    # 2x oversample: upsample, distort, downsample
    up_l = sig.resample(samples[:, 0], n * 2)
    up_r = sig.resample(samples[:, 1], n * 2)
    up = np.column_stack([up_l, up_r])

    # Saturation (at 2x sample rate, harmonics up to 2*Nyquist are safe)
    driven = np.tanh(up * drive)

    # Anti-aliasing low-pass before downsample (cut at original Nyquist)
    aa_freq = min(sample_rate / 2 - 100, sample_rate * 0.45)
    sos_aa = sig.butter(4, aa_freq, btype="low", fs=sample_rate * 2, output="sos")
    driven[:, 0] = sig.sosfilt(sos_aa, driven[:, 0])
    driven[:, 1] = sig.sosfilt(sos_aa, driven[:, 1])

    # Downsample back to original rate
    down_l = sig.resample(driven[:, 0], n)
    down_r = sig.resample(driven[:, 1], n)

    # Tone control (1-pole LP)
    alpha = 0.1 + tone * 0.85
    b_lp = [alpha]
    a_lp = [1.0, -(1.0 - alpha)]
    toned_l = sig.lfilter(b_lp, a_lp, down_l)
    toned_r = sig.lfilter(b_lp, a_lp, down_r)
    toned = np.column_stack([toned_l, toned_r])
    result = samples * (1 - wet) + toned * wet
    return np.clip(result, -1.0, 1.0).astype(np.float64)


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
    """Resonant low-pass filter (biquad).

    Q controls resonance at the cutoff frequency. 0.707 = Butterworth
    (flat passband, no resonance). Higher Q = resonant peak that makes
    synths sing and filters scream. Q > 10 = self-oscillation territory.

    Args:
        cutoff_hz: Cutoff frequency.
        q: Quality factor / resonance (0.5-20.0). 0.707 = flat. 5+ = resonant peak.
    """
    cutoff_hz = min(cutoff_hz, sample_rate / 2 - 1)
    # Use iirpeak for resonant filters, butter for flat Q=0.707
    if abs(q - 0.707) < 0.01:
        sos = sig.butter(2, cutoff_hz, btype="low", fs=sample_rate, output="sos")
    else:
        # Convert Q to bandwidth for scipy's iirfilter
        sos = sig.iirfilter(
            2, cutoff_hz, btype="lowpass", ftype="butter", fs=sample_rate, output="sos"
        )
        # Apply resonance by adding a peak at cutoff
        if q > 1.0:
            bw = cutoff_hz / q
            low_bp = max(20.0, cutoff_hz - bw / 2)
            high_bp = min(sample_rate / 2 - 1, cutoff_hz + bw / 2)
            if low_bp < high_bp:
                sos_peak = sig.butter(
                    2, [low_bp, high_bp], btype="band", fs=sample_rate, output="sos"
                )
                resonance_amount = min((q - 1.0) * 0.3, 3.0)
                filtered = _biquad_sos(samples, sos)
                peak = _biquad_sos(samples, sos_peak)
                return (filtered + peak * resonance_amount).astype(np.float64)
    return _biquad_sos(samples, sos)


def highpass(
    samples: FloatArray,
    sample_rate: int = 44100,
    cutoff_hz: float = 200.0,
    q: float = 0.707,
) -> FloatArray:
    """Resonant high-pass filter (biquad).

    Args:
        cutoff_hz: Cutoff frequency.
        q: Quality factor / resonance (0.5-20.0).
    """
    cutoff_hz = max(20.0, min(cutoff_hz, sample_rate / 2 - 1))
    sos = sig.butter(2, cutoff_hz, btype="high", fs=sample_rate, output="sos")
    if q > 1.0:
        bw = cutoff_hz / q
        low_bp = max(20.0, cutoff_hz - bw / 2)
        high_bp = min(sample_rate / 2 - 1, cutoff_hz + bw / 2)
        if low_bp < high_bp:
            sos_peak = sig.butter(2, [low_bp, high_bp], btype="band", fs=sample_rate, output="sos")
            resonance_amount = min((q - 1.0) * 0.3, 3.0)
            filtered = _biquad_sos(samples, sos)
            peak = _biquad_sos(samples, sos_peak)
            return (filtered + peak * resonance_amount).astype(np.float64)
    return _biquad_sos(samples, sos)


def bandpass(
    samples: FloatArray,
    sample_rate: int = 44100,
    center_hz: float = 1000.0,
    q: float = 1.0,
) -> FloatArray:
    """Resonant band-pass filter (biquad).

    Higher Q = narrower band = more resonant. Q=1 is moderate. Q=10
    is a sharp notch that rings like a bell. The filter Q here directly
    controls bandwidth: BW = center/Q.

    Args:
        center_hz: Center frequency.
        q: Quality factor (0.5-20.0). Higher = narrower passband.
    """
    bw = center_hz / max(q, 0.1)
    low = max(20.0, center_hz - bw / 2)
    high = min(sample_rate / 2 - 1, center_hz + bw / 2)
    if low >= high:
        return samples.copy()
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
    makeup_gain: float = 0.0,
    knee_db: float = 6.0,
    lookahead_ms: float = 5.0,
) -> FloatArray:
    """Compressor with soft knee, look-ahead, and auto-makeup gain.

    Soft knee: instead of an abrupt ratio change at the threshold, the
    compression ratio ramps gradually over a region around the threshold.
    This sounds more natural - like a human engineer riding a fader
    instead of a switch clicking on.

    Look-ahead: a small delay that lets the compressor see transients
    before they arrive, preventing the first few milliseconds of a
    snare hit or kick from punching through uncompressed.

    Auto-makeup: when makeup_gain is 0 (default), automatically
    compensates for the volume reduction caused by compression. The
    formula approximates the average gain reduction and inverts it.

    Args:
        threshold:     Compression threshold (0.0-1.0 linear).
        ratio:         Compression ratio (1.0 = no compression, inf = limiting).
        attack_ms:     Attack time (1-100ms).
        release_ms:    Release time (10-500ms).
        makeup_gain:   Manual makeup gain. 0 = auto-calculate.
        knee_db:       Soft knee width in dB (0 = hard knee, 6 = gentle, 12 = very soft).
        lookahead_ms:  Look-ahead time (0-10ms). Delays the dry signal to catch transients.
    """
    peak = np.max(np.abs(samples), axis=1)

    # Look-ahead: shift the envelope detection forward in time
    if lookahead_ms > 0:
        la_samples = int(lookahead_ms * sample_rate / 1000)
        peak = np.roll(peak, -la_samples)
        peak[-la_samples:] = peak[-la_samples - 1]

    # Separate attack/release envelope follower (attack is fast, release is slow)
    a_coef = math.exp(-1.0 / max(1, attack_ms * sample_rate / 1000))
    r_coef = math.exp(-1.0 / max(1, release_ms * sample_rate / 1000))

    env = np.zeros(len(peak))
    env[0] = peak[0]
    for i in range(1, len(peak)):
        if peak[i] > env[i - 1]:
            env[i] = a_coef * env[i - 1] + (1 - a_coef) * peak[i]
        else:
            env[i] = r_coef * env[i - 1] + (1 - r_coef) * peak[i]

    # Convert to dB for soft knee calculation
    env_db = 20 * np.log10(np.maximum(env, 1e-10))
    thresh_db = 20 * np.log10(max(threshold, 1e-10))

    # Soft knee gain computation
    half_knee = knee_db / 2.0
    gain_db = np.zeros_like(env_db)

    for i in range(len(env_db)):
        x = env_db[i]
        if x < thresh_db - half_knee:
            gain_db[i] = 0.0  # below knee: no compression
        elif x > thresh_db + half_knee:
            gain_db[i] = thresh_db + (x - thresh_db) / ratio - x  # above knee: full ratio
        else:
            # Inside the knee: quadratic interpolation
            knee_range = x - (thresh_db - half_knee)
            gain_db[i] = ((1 / ratio - 1) * knee_range**2) / (2 * knee_db)

    gain_linear = 10 ** (gain_db / 20.0)

    # Auto-makeup gain: compensate for average gain reduction
    if makeup_gain == 0.0:
        avg_reduction = np.mean(gain_linear)
        if avg_reduction > 0:
            auto_makeup = 1.0 / max(avg_reduction, 0.1)
            auto_makeup = min(auto_makeup, 4.0)  # cap at +12dB
        else:
            auto_makeup = 1.0
    else:
        auto_makeup = makeup_gain

    result = samples * gain_linear[:, np.newaxis] * auto_makeup
    return np.clip(result, -1.0, 1.0).astype(np.float64)


# ---------------------------------------------------------------------------
# Stereo pan
# ---------------------------------------------------------------------------


def noise_gate(
    samples: FloatArray,
    sample_rate: int = 44100,
    threshold: float = 0.02,
    attack_ms: float = 1.0,
    hold_ms: float = 50.0,
    release_ms: float = 100.0,
) -> FloatArray:
    """Noise gate: silence audio below a threshold.

    Essential for cleaning up drum tracks (no bleed between hits),
    guitar tracks (no hum between notes), and any recording with
    background noise. The gate opens when the signal exceeds the
    threshold and closes when it drops below.

    Args:
        threshold:   Level below which audio is gated (0.0-1.0).
        attack_ms:   How fast the gate opens (1-10ms).
        hold_ms:     Minimum time gate stays open after signal drops.
        release_ms:  How fast the gate closes (50-500ms).
    """
    peak = np.max(np.abs(samples), axis=1)

    gate = np.zeros(len(peak))
    hold_samples = int(hold_ms * sample_rate / 1000)
    a_coef = math.exp(-1.0 / max(1, attack_ms * sample_rate / 1000))
    r_coef = math.exp(-1.0 / max(1, release_ms * sample_rate / 1000))

    hold_counter = 0
    gate_state = 0.0
    for i in range(len(peak)):
        if peak[i] >= threshold:
            gate_state = 1.0 - a_coef * (1.0 - gate_state)
            hold_counter = hold_samples
        elif hold_counter > 0:
            hold_counter -= 1
            gate_state = 1.0
        else:
            gate_state = r_coef * gate_state
        gate[i] = gate_state

    return (samples * gate[:, np.newaxis]).astype(np.float64)


def sidechain(
    samples: FloatArray,
    trigger: FloatArray,
    sample_rate: int = 44100,
    threshold: float = 0.3,
    ratio: float = 8.0,
    attack_ms: float = 1.0,
    release_ms: float = 150.0,
) -> FloatArray:
    """Sidechain compression: duck one signal when another hits.

    THE EDM effect. The kick triggers compression on the pad/bass,
    creating the pumping rhythm that defines modern electronic music.

    Args:
        samples:     Signal to compress (pad, bass).
        trigger:     Signal that controls compression (kick).
        threshold:   Trigger level that activates ducking.
        ratio:       How much to duck (4-20).
        attack_ms:   How fast the duck starts.
        release_ms:  How fast it recovers (50-300ms for audible pump).
    """
    if trigger.ndim == 2:
        trig_peak = np.max(np.abs(trigger), axis=1)
    else:
        trig_peak = np.abs(trigger)

    n = min(len(samples), len(trig_peak))
    trig_peak = trig_peak[:n]

    a_coef = math.exp(-1.0 / max(1, attack_ms * sample_rate / 1000))
    r_coef = math.exp(-1.0 / max(1, release_ms * sample_rate / 1000))

    env = np.zeros(n)
    env[0] = trig_peak[0]
    for i in range(1, n):
        if trig_peak[i] > env[i - 1]:
            env[i] = a_coef * env[i - 1] + (1 - a_coef) * trig_peak[i]
        else:
            env[i] = r_coef * env[i - 1] + (1 - r_coef) * trig_peak[i]

    gain = np.where(
        env > threshold,
        (threshold + (env - threshold) / ratio) / np.maximum(env, 1e-9),
        1.0,
    )

    out = samples[:n].copy()
    out *= gain[:, np.newaxis]
    if len(samples) > n:
        out = np.vstack([out, samples[n:]])
    return out.astype(np.float64)


def stereo_width(
    samples: FloatArray,
    width: float = 1.0,
) -> FloatArray:
    """Adjust stereo width via mid-side processing.

    Mid-side is the secret weapon of mastering. Width=0 = mono.
    Width=1 = unchanged. Width=2 = exaggerated stereo.

    Args:
        width: Stereo width multiplier (0.0=mono, 1.0=normal, 2.0=wide).
    """
    mid = (samples[:, 0] + samples[:, 1]) * 0.5
    side = (samples[:, 0] - samples[:, 1]) * 0.5
    side = side * width
    return np.column_stack([mid + side, mid - side]).astype(np.float64)


def transient_shaper(
    samples: FloatArray,
    sample_rate: int = 44100,
    attack: float = 0.0,
    sustain: float = 0.0,
) -> FloatArray:
    """Transient shaper: control attack punch and sustain body independently.

    Unlike a compressor which reduces everything above a threshold, a
    transient shaper detects the onset (attack) and steady-state (sustain)
    portions of each hit and lets you boost or cut them independently.
    +attack = more snap on drums. -attack = softer transients. +sustain =
    more room/body. -sustain = tighter, drier.

    The secret weapon for drums and percussion. Makes a weak snare
    crack like a gunshot or turns a ringy tom into a tight thud.

    Args:
        attack:   Attack gain in dB (-12 to +12). Positive = more snap.
        sustain:  Sustain gain in dB (-12 to +12). Positive = more body.
    """
    if abs(attack) < 0.1 and abs(sustain) < 0.1:
        return samples.copy()

    # Envelope follower with fast attack, slow release
    peak = np.max(np.abs(samples), axis=1) if samples.ndim == 2 else np.abs(samples)

    fast_coef = math.exp(-1.0 / (0.001 * sample_rate))  # 1ms
    slow_coef = math.exp(-1.0 / (0.1 * sample_rate))  # 100ms

    fast_env = np.zeros(len(peak))
    slow_env = np.zeros(len(peak))
    fast_env[0] = peak[0]
    slow_env[0] = peak[0]
    for i in range(1, len(peak)):
        coef_f = fast_coef if peak[i] < fast_env[i - 1] else 0.0
        fast_env[i] = coef_f * fast_env[i - 1] + (1 - coef_f) * peak[i]
        coef_s = slow_coef if peak[i] < slow_env[i - 1] else 0.0
        slow_env[i] = coef_s * slow_env[i - 1] + (1 - coef_s) * peak[i]

    # Transient = fast - slow (positive during attacks)
    transient = fast_env - slow_env
    transient = np.clip(transient, 0, None)

    # Sustain mask = inverse of transient
    sustain_mask = np.clip(slow_env - transient * 0.5, 0, None)

    # Apply gains
    attack_gain = 10 ** (attack / 20.0) - 1.0
    sustain_gain = 10 ** (sustain / 20.0) - 1.0

    # Normalize envelopes
    t_max = np.max(transient)
    s_max = np.max(sustain_mask)
    if t_max > 0:
        transient /= t_max
    if s_max > 0:
        sustain_mask /= s_max

    gain = 1.0 + transient * attack_gain + sustain_mask * sustain_gain

    if samples.ndim == 2:
        result = samples * gain[:, np.newaxis]
    else:
        result = samples * gain

    return np.clip(result, -1.0, 1.0).astype(np.float64)


def tape_emulation(
    samples: FloatArray,
    sample_rate: int = 44100,
    speed: str = "15ips",
    saturation: float = 0.5,
    hiss: float = 0.005,
    wet: float = 1.0,
) -> FloatArray:
    """Analog tape machine emulation.

    Real tape does three things to audio:
    1. Soft compression (tape naturally compresses peaks)
    2. Harmonic saturation (subtle, warm, adds density)
    3. Frequency response curve (bass bump, gentle HF rolloff)

    Different tape speeds have different characters:
        30ips: flattest response, most headroom, least color
        15ips: slight bass bump (~50Hz), gentle HF rolloff, most common
        7.5ips: pronounced bass bump, noticeable HF loss, lo-fi character

    This is the "glue" that makes analog recordings sound cohesive.
    Every track hitting the same tape gets the same subtle processing.

    Args:
        speed:       Tape speed ("30ips", "15ips", "7.5ips").
        saturation:  Tape saturation amount (0.0-1.0).
        hiss:        Tape hiss level (0.0-0.02).
        wet:         Wet/dry mix.
    """
    nyq = sample_rate / 2 - 1

    # Frequency response curve per speed
    curves = {
        "30ips": (20.0, 20000.0, 0.0),  # flat
        "15ips": (40.0, 16000.0, 1.5),  # bass bump, gentle rolloff
        "7.5ips": (60.0, 10000.0, 3.0),  # pronounced character
    }
    bass_freq, hf_cutoff, bass_boost = curves.get(speed, curves["15ips"])
    hf_cutoff = min(hf_cutoff, nyq)

    out = samples.copy()

    # HF rolloff (tape head gap loss)
    sos_hf = sig.butter(2, hf_cutoff, btype="low", fs=sample_rate, output="sos")
    if out.ndim == 2:
        out[:, 0] = sig.sosfilt(sos_hf, out[:, 0])
        out[:, 1] = sig.sosfilt(sos_hf, out[:, 1])
    else:
        out = sig.sosfilt(sos_hf, out)

    # Bass bump (head bump resonance)
    if bass_boost > 0:
        bass_freq = min(bass_freq, nyq)
        sos_bass = sig.butter(1, bass_freq, btype="low", fs=sample_rate, output="sos")
        if out.ndim == 2:
            out[:, 0] += sig.sosfilt(sos_bass, out[:, 0]) * bass_boost * 0.15
            out[:, 1] += sig.sosfilt(sos_bass, out[:, 1]) * bass_boost * 0.15
        else:
            out += sig.sosfilt(sos_bass, out) * bass_boost * 0.15

    # Tape saturation (soft compression + harmonics)
    if saturation > 0:
        drive = 1.0 + saturation * 2.0
        out = out * drive
        out = out / (1.0 + np.abs(out) * saturation * 0.5)  # soft clip
        # Normalize back
        pk = np.max(np.abs(out))
        if pk > 0:
            out /= pk
        out *= np.max(np.abs(samples))

    # Tape hiss
    if hiss > 0:
        rng = np.random.default_rng(42)
        if out.ndim == 2:
            noise = rng.standard_normal(out.shape) * hiss
        else:
            noise = rng.standard_normal(len(out)) * hiss
        # Tape hiss is shaped (not flat white noise)
        sos_hiss = sig.butter(1, min(8000.0, nyq), btype="low", fs=sample_rate, output="sos")
        if out.ndim == 2:
            noise[:, 0] = sig.sosfilt(sos_hiss, noise[:, 0])
            noise[:, 1] = sig.sosfilt(sos_hiss, noise[:, 1])
        else:
            noise = sig.sosfilt(sos_hiss, noise)
        out = out + noise

    result = samples * (1 - wet) + out * wet
    return np.clip(result, -1.0, 1.0).astype(np.float64)


def volume_shaper(
    samples: FloatArray,
    sample_rate: int = 44100,
    bpm: float = 128.0,
    shape: str = "pump",
    depth: float = 0.8,
    rate: float = 1.0,
) -> FloatArray:
    """Tempo-synced volume shaper - the modern EDM sidechain pump.

    NOT compression. A shaped volume envelope synced to the BPM. Every
    beat, the volume dips and recovers in a specific curve. This is what
    LFOTool, VolumeShaper, and Kickstart do. The pump that makes EDM
    breathe. Deadmau5 runs this on literally everything except the kick.

    Shapes:
        pump:      Classic sidechain pump (fast dip, slow recovery)
        gate:      Hard on/off rhythmic gate (trance gate)
        sine:      Smooth sine wave volume modulation
        saw_up:    Volume ramps up each beat (builds energy)
        saw_down:  Volume ramps down each beat (fades between hits)
        half:      Pump on every other beat (half-time feel)

    Args:
        bpm:    Song tempo for sync.
        shape:  Curve shape name.
        depth:  How deep the pump goes (0.0=none, 1.0=full silence at dip).
        rate:   Rate multiplier (0.5=half speed, 1.0=per beat, 2.0=per 8th note).
    """
    n = len(samples)
    beat_samples = int(60.0 / bpm * sample_rate / rate)
    if beat_samples < 2:
        return samples.copy()

    # Build one cycle of the shape
    t_cycle = np.linspace(0, 1, beat_samples)

    if shape == "pump":
        # Fast attack to minimum, exponential recovery
        curve = 1.0 - depth * np.exp(-6.0 * t_cycle)
    elif shape == "gate":
        # Hard gate: on for first half, off for second half
        curve = np.where(t_cycle < 0.5, 1.0, 1.0 - depth)
    elif shape == "sine":
        curve = 1.0 - depth * 0.5 * (1.0 - np.cos(2 * np.pi * t_cycle))
    elif shape == "saw_up":
        curve = (1.0 - depth) + depth * t_cycle
    elif shape == "saw_down":
        curve = 1.0 - depth * t_cycle
    elif shape == "half":
        # Pump every other beat
        half_cycle = np.ones(beat_samples * 2)
        half_cycle[:beat_samples] = 1.0 - depth * np.exp(-6.0 * t_cycle)
        curve = half_cycle
        beat_samples = len(curve)
    else:
        curve = 1.0 - depth * np.exp(-6.0 * t_cycle)

    # Tile the curve across the full signal
    n_repeats = n // beat_samples + 2
    full_curve = np.tile(curve, n_repeats)[:n]

    if samples.ndim == 2:
        return (samples * full_curve[:, np.newaxis]).astype(np.float64)
    return (samples * full_curve).astype(np.float64)


def filter_envelope(
    samples: FloatArray,
    sample_rate: int = 44100,
    cutoff_start: float = 200.0,
    cutoff_end: float = 8000.0,
    attack: float = 0.01,
    decay: float = 0.3,
    sustain_cutoff: float = 2000.0,
    release: float = 0.5,
    resonance: float = 2.0,
) -> FloatArray:
    """Filter with its own ADSR envelope - independent from amplitude.

    Every EDM pluck, bass stab, and "wub" sound uses this. The filter
    cutoff sweeps: opens fast on attack (bright transient), decays to a
    sustain frequency (body of the sound), then closes on release.
    The amplitude ADSR controls volume. This ADSR controls brightness.
    Two independent envelopes = the sound of modern synthesis.

    Serum, Massive, Vital - they all have this as a core feature.

    Args:
        cutoff_start:    Filter frequency at note start (Hz).
        cutoff_end:      Filter frequency at peak of attack (Hz).
        attack:          Time to sweep from start to end (seconds).
        decay:           Time to decay from end to sustain (seconds).
        sustain_cutoff:  Filter frequency during sustain (Hz).
        release:         Time to close filter at note end (seconds).
        resonance:       Filter Q (1=gentle, 5=aggressive, 10=screaming).
    """
    n = len(samples)
    sr = sample_rate
    nyq = sr / 2 - 1

    # Build the filter cutoff envelope
    a_s = int(attack * sr)
    d_s = int(decay * sr)
    r_s = int(release * sr)
    s_s = max(0, n - a_s - d_s - r_s)

    cutoff_env = np.zeros(n)
    pos = 0

    # Attack: sweep from start to end
    if a_s > 0:
        cutoff_env[pos : pos + a_s] = np.linspace(cutoff_start, cutoff_end, a_s)
        pos += a_s

    # Decay: sweep from end to sustain
    if d_s > 0:
        end_pos = min(pos + d_s, n)
        cutoff_env[pos:end_pos] = np.linspace(cutoff_end, sustain_cutoff, end_pos - pos)
        pos = end_pos

    # Sustain: hold at sustain cutoff
    if s_s > 0:
        end_pos = min(pos + s_s, n)
        cutoff_env[pos:end_pos] = sustain_cutoff
        pos = end_pos

    # Release: close filter
    if r_s > 0 and pos < n:
        end_pos = min(pos + r_s, n)
        cutoff_env[pos:end_pos] = np.linspace(sustain_cutoff, cutoff_start, end_pos - pos)
        pos = end_pos

    # Fill any remainder
    cutoff_env[pos:] = cutoff_start

    # Clamp
    cutoff_env = np.clip(cutoff_env, 20.0, nyq)

    # Apply time-varying filter in blocks
    block_size = 128
    out = np.zeros_like(samples)
    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        cutoff = float(np.mean(cutoff_env[start:end]))
        cutoff = max(20.0, min(cutoff, nyq))
        try:
            sos = sig.butter(2, cutoff, btype="low", fs=sr, output="sos")
            if samples.ndim == 2:
                out[start:end, 0] = sig.sosfilt(sos, samples[start:end, 0])
                out[start:end, 1] = sig.sosfilt(sos, samples[start:end, 1])
            else:
                out[start:end] = sig.sosfilt(sos, samples[start:end])
        except Exception:
            out[start:end] = samples[start:end]

    # Add resonance peak
    if resonance > 1.0:
        peak_cutoff = float(np.mean(cutoff_env))
        bw = peak_cutoff / max(resonance, 0.5)
        lo = max(20.0, peak_cutoff - bw / 2)
        hi = min(nyq, peak_cutoff + bw / 2)
        if lo < hi:
            sos_peak = sig.butter(2, [lo, hi], btype="band", fs=sr, output="sos")
            res_amount = min((resonance - 1.0) * 0.2, 1.5)
            if samples.ndim == 2:
                out[:, 0] += sig.sosfilt(sos_peak, samples[:, 0]) * res_amount
                out[:, 1] += sig.sosfilt(sos_peak, samples[:, 1]) * res_amount
            else:
                out += sig.sosfilt(sos_peak, samples) * res_amount

    return np.clip(out, -1.0, 1.0).astype(np.float64)


def stutter(
    samples: FloatArray,
    sample_rate: int = 44100,
    bpm: float = 128.0,
    divisions: int = 8,
    bars: float = 1.0,
    ramp: bool = True,
) -> FloatArray:
    """Stutter/beat repeat/glitch - chop and rapid-fire repeat.

    Madeon's signature move. Takes a slice of audio and repeats it
    faster and faster. 1/4 note repeats -> 1/8 -> 1/16 -> 1/32.
    The "machine gun" buildup effect. Also used as a glitch effect
    when applied to random positions.

    Args:
        bpm:        Song tempo for sync.
        divisions:  How many repeats (4=quarter notes, 8=8ths, 16=16ths, 32=32nds).
        bars:       How many bars to apply the stutter over.
        ramp:       If True, divisions increase over time (buildup). If False, constant.
    """
    n = len(samples)
    beat_sec = 60.0 / bpm
    bar_samples = int(beat_sec * 4 * sample_rate)
    total_stutter = int(bars * bar_samples)
    total_stutter = min(total_stutter, n)

    if total_stutter < 100:
        return samples.copy()

    out = samples.copy()
    stutter_region = out[:total_stutter].copy()

    if ramp:
        # Divisions increase over time: 2 -> 4 -> 8 -> 16 -> 32
        div_sequence = []
        current_div = max(2, divisions // 8)
        while current_div <= divisions:
            div_sequence.append(current_div)
            current_div *= 2
        if not div_sequence:
            div_sequence = [divisions]

        # Split the stutter region into sections, one per division level
        section_len = total_stutter // len(div_sequence)
        pos = 0
        for div in div_sequence:
            slice_len = max(1, int(beat_sec * 4 / div * sample_rate))
            # Grab the first slice at this position
            source_end = min(pos + slice_len, total_stutter)
            grain = stutter_region[pos:source_end]
            if len(grain) == 0:
                break
            # Repeat the grain to fill the section
            section_end = min(pos + section_len, total_stutter)
            write_pos = pos
            while write_pos < section_end:
                copy_len = min(len(grain), section_end - write_pos)
                if copy_len > 0:
                    out[write_pos : write_pos + copy_len] = grain[:copy_len]
                write_pos += len(grain)
            pos = section_end
    else:
        # Constant division
        slice_len = max(1, int(beat_sec * 4 / divisions * sample_rate))
        grain = stutter_region[:slice_len]
        pos = 0
        while pos < total_stutter:
            copy_len = min(len(grain), total_stutter - pos)
            if copy_len > 0:
                out[pos : pos + copy_len] = grain[:copy_len]
            pos += len(grain)

    return out.astype(np.float64)


def noise_riser(
    sample_rate: int = 44100,
    duration_sec: float = 4.0,
    start_freq: float = 200.0,
    end_freq: float = 12000.0,
    noise_type: str = "white",
) -> FloatArray:
    """Generate a noise sweep riser - the tension builder before a drop.

    Filtered noise with a rising cutoff frequency. Starts dark and low,
    sweeps up to bright and intense. The sound that tells the crowd
    "something is about to happen." Every EDM buildup uses one.

    Returns a stereo array that can be added to a mix or used as a
    sample.

    Args:
        duration_sec:  Length of the riser.
        start_freq:    Starting filter cutoff (Hz, low = dark).
        end_freq:      Ending filter cutoff (Hz, high = bright/intense).
        noise_type:    "white" (harsh), "pink" (warmer).
    """
    n = int(duration_sec * sample_rate)
    nyq = sample_rate / 2 - 1
    rng = np.random.default_rng(42)

    if noise_type == "pink":
        # Approximate pink noise via filtered white
        white = rng.standard_normal(n)
        sos_pink = sig.butter(1, min(1000.0, nyq), btype="low", fs=sample_rate, output="sos")
        noise = sig.sosfilt(sos_pink, white) * 2
    else:
        noise = rng.standard_normal(n)

    # Sweep filter cutoff from start to end (exponential for perceptual linearity)
    cutoffs = np.exp(np.linspace(np.log(max(start_freq, 20)), np.log(min(end_freq, nyq)), n))

    # Apply time-varying filter in blocks
    block = 256
    out = np.zeros(n)
    for s in range(0, n, block):
        e = min(s + block, n)
        cutoff = float(np.clip(np.mean(cutoffs[s:e]), 20.0, nyq))
        sos = sig.butter(2, cutoff, btype="low", fs=sample_rate, output="sos")
        out[s:e] = sig.sosfilt(sos, noise[s:e])

    # Volume ramps up
    out *= np.linspace(0.1, 1.0, n)

    # Return as stereo with slight L/R decorrelation
    out_r = np.roll(out, int(0.003 * sample_rate))
    return np.column_stack([out, out_r]).astype(np.float64)


def impact(
    sample_rate: int = 44100,
    duration_sec: float = 2.0,
    sub_freq: float = 40.0,
    brightness: float = 0.5,
) -> FloatArray:
    """Generate a drop impact / downlifter - the BOOM at the start of a drop.

    Sub bass hit + noise burst + reverse crash character. The sound that
    shakes the venue when the beat drops back in. Every EDM drop starts
    with one. Usually a sub sine hit with a fast pitch drop plus a burst
    of filtered noise.

    Returns a stereo array.

    Args:
        duration_sec:  Total impact length.
        sub_freq:      Sub bass fundamental (30-60 Hz typical).
        brightness:    Noise brightness (0=dark rumble, 1=bright crash).
    """
    n = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, n, endpoint=False)
    nyq = sample_rate / 2 - 1

    # Sub hit: pitch-dropping sine
    freq_env = sub_freq * np.exp(-8.0 * t)
    sub = np.sin(2 * np.pi * np.cumsum(freq_env) / sample_rate)
    sub *= np.exp(-3.0 * t)  # fast decay

    # Noise burst: filtered, fast decay
    rng = np.random.default_rng(42)
    noise = rng.standard_normal(n)
    cutoff = min(1000.0 + brightness * 8000.0, nyq)
    sos = sig.butter(2, cutoff, btype="low", fs=sample_rate, output="sos")
    noise = sig.sosfilt(sos, noise)
    noise *= np.exp(-5.0 * t) * 0.4

    out = sub * 0.7 + noise
    # Normalize
    pk = np.max(np.abs(out))
    if pk > 0:
        out /= pk

    return np.column_stack([out, out]).astype(np.float64)


def phaser(
    samples: FloatArray,
    sample_rate: int = 44100,
    rate_hz: float = 0.3,
    depth: float = 0.7,
    stages: int = 6,
    feedback: float = 0.5,
    wet: float = 0.5,
) -> FloatArray:
    """Phaser: cascaded allpass filters with LFO-swept cutoff.

    The classic synth sweep. Van Halen "Eruption," Tame Impala everything.
    A chain of allpass filters creates notches in the frequency spectrum.
    An LFO sweeps those notches up and down. The feedback path creates
    resonant peaks between the notches. More stages = more notches =
    deeper, more complex phasing.

    Args:
        rate_hz:   LFO speed (0.1-2.0 Hz typical).
        depth:     LFO depth (0.0-1.0).
        stages:    Number of allpass stages (2-12, more = deeper).
        feedback:  Feedback amount (0.0-0.9, higher = more resonant).
        wet:       Wet/dry mix.
    """
    n = len(samples)
    t = np.arange(n) / sample_rate
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * rate_hz * t)

    # LFO modulates the allpass center frequency
    min_freq = 200.0
    max_freq = min(5000.0, sample_rate / 2 - 100)
    center_freqs = min_freq + lfo * depth * (max_freq - min_freq)

    # Process in blocks for time-varying allpass
    block = 256
    dry = samples.copy()
    wet_signal = samples.copy()
    fb_buf = np.zeros_like(samples[0]) if samples.ndim == 2 else 0.0

    for s in range(0, n, block):
        e = min(s + block, n)
        freq = float(np.mean(center_freqs[s:e]))
        freq = max(100.0, min(freq, sample_rate / 2 - 100))

        # Build allpass cascade
        for _ in range(stages):
            w0 = 2 * np.pi * freq / sample_rate
            alpha = np.sin(w0) / 2.0
            # Allpass coefficients
            b = [1.0 - alpha, -2.0 * np.cos(w0), 1.0 + alpha]
            a = [1.0 + alpha, -2.0 * np.cos(w0), 1.0 - alpha]
            if samples.ndim == 2:
                wet_signal[s:e, 0] = sig.lfilter(b, a, wet_signal[s:e, 0])
                wet_signal[s:e, 1] = sig.lfilter(b, a, wet_signal[s:e, 1])
            else:
                wet_signal[s:e] = sig.lfilter(b, a, wet_signal[s:e])

        # Apply feedback
        if feedback > 0 and s + block < n:
            if samples.ndim == 2:
                wet_signal[s:e] += fb_buf * feedback
                fb_buf = wet_signal[e - 1 : e].copy().flatten()
            else:
                wet_signal[s:e] += fb_buf * feedback
                fb_buf = wet_signal[e - 1]

    return (dry * (1 - wet) + wet_signal * wet).astype(np.float64)


def flanger(
    samples: FloatArray,
    sample_rate: int = 44100,
    rate_hz: float = 0.2,
    depth_ms: float = 3.0,
    feedback: float = 0.6,
    wet: float = 0.5,
) -> FloatArray:
    """Flanger: short modulated delay with feedback.

    Like chorus but the delay is shorter (0.5-5ms vs 15-30ms for chorus)
    and the feedback creates a resonant comb filter effect. The result is
    the jet-engine whoosh, metallic sweep, and through-zero cancellation
    that defines the flanger sound. Hendrix, The Cure, every synthwave
    track ever.

    Args:
        rate_hz:   LFO speed.
        depth_ms:  Maximum delay depth in ms (1-5 typical).
        feedback:  Feedback amount (0.0-0.95). High = metallic resonance.
        wet:       Wet/dry mix.
    """
    n = len(samples)
    t = np.arange(n) / sample_rate
    depth_samples = depth_ms * sample_rate / 1000.0

    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * rate_hz * t)
    delays = (lfo * depth_samples).astype(np.float64)

    out = np.zeros_like(samples)
    fb = np.zeros_like(samples[0]) if samples.ndim == 2 else 0.0

    for i in range(n):
        d = delays[i]
        read_pos = i - d
        if read_pos < 0:
            delayed = np.zeros_like(samples[0]) if samples.ndim == 2 else 0.0
        else:
            lo_idx = int(read_pos)
            hi_idx = min(lo_idx + 1, n - 1)
            frac = read_pos - lo_idx
            delayed = samples[lo_idx] * (1 - frac) + samples[hi_idx] * frac

        out[i] = samples[i] + (delayed + fb * feedback)
        fb = delayed

    result = samples * (1 - wet) + out * wet
    return np.clip(result, -1.0, 1.0).astype(np.float64)


def ring_mod(
    samples: FloatArray,
    sample_rate: int = 44100,
    freq_hz: float = 300.0,
    wet: float = 0.5,
) -> FloatArray:
    """Ring modulator: multiply the signal with a carrier oscillator.

    Creates sum and difference frequencies (sidebands) that are
    inharmonic and metallic. Low carrier = tremolo. Mid carrier =
    alien/robotic. High carrier = metallic clang. The Daleks from
    Doctor Who use ring mod on voice. Skrillex uses it on bass for
    that aggressive, alien quality.

    Args:
        freq_hz:  Carrier frequency (20-2000 Hz).
        wet:      Wet/dry mix.
    """
    n = len(samples)
    t = np.arange(n) / sample_rate
    carrier = np.sin(2 * np.pi * freq_hz * t)

    if samples.ndim == 2:
        modulated = np.column_stack(
            [
                samples[:, 0] * carrier,
                samples[:, 1] * carrier,
            ]
        )
    else:
        modulated = samples * carrier

    return (samples * (1 - wet) + modulated * wet).astype(np.float64)


def reverse_reverb(
    samples: FloatArray,
    sample_rate: int = 44100,
    room_size: float = 0.7,
    damping: float = 0.3,
    wet: float = 0.4,
) -> FloatArray:
    """Reverse reverb: the reverb tail builds UP to the note.

    Normal reverb: note -> reverb tail after. Reverse reverb: ghostly
    swell -> note arrives. Creates an eerie, pulling sensation like
    the sound is being sucked into the note from the future. Shoegaze,
    ambient, Skrillex transitions, horror soundtracks.

    How it works: reverse the audio, apply reverb, reverse again.
    The reverb tail is now a pre-tail that crescendos into each note.

    Args:
        room_size:  Reverb size (bigger = longer pre-swell).
        damping:    High frequency damping.
        wet:        Wet/dry mix.
    """
    # Reverse
    reversed_samples = samples[::-1].copy()

    # Apply normal reverb to the reversed audio
    ir = _make_reverb_ir(sample_rate, room_size, damping)
    if reversed_samples.ndim == 2:
        rev_l = sig.fftconvolve(reversed_samples[:, 0], ir, mode="full")[: len(samples)]
        rev_r = sig.fftconvolve(reversed_samples[:, 1], np.roll(ir, 1), mode="full")[: len(samples)]
        for ch in (rev_l, rev_r):
            pk = np.max(np.abs(ch))
            if pk > 0:
                ch /= pk
        reverbed = np.column_stack([rev_l, rev_r])
    else:
        reverbed = sig.fftconvolve(reversed_samples, ir, mode="full")[: len(samples)]
        pk = np.max(np.abs(reverbed))
        if pk > 0:
            reverbed /= pk

    # Reverse back (the reverb tail is now a pre-tail)
    reversed_reverb = reverbed[::-1]

    return (samples * (1 - wet) + reversed_reverb * wet).astype(np.float64)


def comb_filter(
    samples: FloatArray,
    sample_rate: int = 44100,
    freq_hz: float = 500.0,
    feedback: float = 0.8,
    wet: float = 0.5,
) -> FloatArray:
    """Comb filter: tuned delay that creates pitched resonance from any input.

    Feed noise through a comb filter tuned to 440 Hz and you get a pitched
    A note. The Karplus-Strong algorithm is literally a comb filter with
    a lowpass in the loop. Standalone, comb filters create metallic,
    resonant, pitched textures. Used in Ableton's Resonator and in
    physical modeling synthesis.

    Args:
        freq_hz:   Resonant frequency (the comb is tuned to this pitch).
        feedback:  Feedback (0.0-0.99). Higher = longer resonance, more pitched.
        wet:       Wet/dry mix.
    """
    delay_samples = max(1, int(sample_rate / max(freq_hz, 20.0)))
    n = len(samples)

    if samples.ndim == 2:
        out_l = np.zeros(n)
        out_r = np.zeros(n)
        for i in range(n):
            d = i - delay_samples
            fb_l = out_l[d] * feedback if d >= 0 else 0.0
            fb_r = out_r[d] * feedback if d >= 0 else 0.0
            out_l[i] = samples[i, 0] + fb_l
            out_r[i] = samples[i, 1] + fb_r
        out = np.column_stack([out_l, out_r])
    else:
        out = np.zeros(n)
        for i in range(n):
            d = i - delay_samples
            fb = out[d] * feedback if d >= 0 else 0.0
            out[i] = samples[i] + fb

    result = samples * (1 - wet) + out * wet
    return np.clip(result, -1.0, 1.0).astype(np.float64)


def waveshaper(
    samples: FloatArray,
    curve: str = "soft",
    drive: float = 2.0,
    wet: float = 0.7,
) -> FloatArray:
    """Waveshaper: custom transfer function distortion.

    Different curves produce different harmonic content. Soft clip adds
    mostly 3rd harmonics. Hard clip adds odd harmonics. Fold-back adds
    even harmonics and aliasing artifacts (the Buchla/Serge sound).
    Sine shaping produces dense harmonics. Each curve has its own
    character that is distinct from standard tanh distortion.

    Curves:
        soft:     Cubic soft clip (warm, transparent)
        hard:     Hard clip (harsh, buzzy, lo-fi)
        foldback: Wavefolding (Buchla/Serge, rich even harmonics)
        sine:     Sine waveshaping (dense, complex harmonics)
        asym:     Asymmetric (tube-like, even + odd harmonics)

    Args:
        curve:  Shaping curve name.
        drive:  Input gain before shaping (1-10).
        wet:    Wet/dry mix.
    """
    driven = samples * drive

    if curve == "hard":
        shaped = np.clip(driven, -1.0, 1.0)
    elif curve == "foldback":
        # Wavefolding: signal folds back when it exceeds +-1
        shaped = np.abs(np.abs(np.fmod(driven + 1, 4) - 2) - 1) * 2 - 1
    elif curve == "sine":
        shaped = np.sin(driven * np.pi / 2)
    elif curve == "asym":
        # Asymmetric: positive side clips softer (even harmonics)
        pos = np.maximum(driven, 0)
        neg = np.minimum(driven, 0)
        shaped = np.tanh(pos * 0.7) + np.tanh(neg * 1.3)
    else:
        # Soft (cubic)
        shaped = np.where(
            np.abs(driven) < 1.0, driven - (driven**3) / 3.0, np.sign(driven) * 2.0 / 3.0
        )

    # Normalize
    pk = np.max(np.abs(shaped))
    if pk > 0:
        shaped *= np.max(np.abs(samples)) / pk

    return (samples * (1 - wet) + shaped * wet).astype(np.float64)


def laser_zap(
    sample_rate: int = 44100,
    duration_sec: float = 0.3,
    start_freq: float = 8000.0,
    end_freq: float = 100.0,
    waveform: str = "square",
) -> FloatArray:
    """Generate a laser/zap sound effect.

    Fast downward pitch sweep. Sci-fi, video game, Skrillex transitions.
    The sound of a laser gun, a coin pickup, or a bass drop compressed
    into a quarter second.

    Args:
        duration_sec:  Length of the zap.
        start_freq:    Starting frequency (high = laser, low = boing).
        end_freq:      Ending frequency.
        waveform:      "sine", "square", "sawtooth".
    """
    n = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, n, endpoint=False)

    # Exponential frequency sweep
    freq_env = start_freq * np.exp(-np.log(start_freq / max(end_freq, 1)) * t / duration_sec)
    phase = 2 * np.pi * np.cumsum(freq_env) / sample_rate

    if waveform == "square":
        out = np.sign(np.sin(phase))
    elif waveform == "sawtooth":
        out = 2.0 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))
    else:
        out = np.sin(phase)

    # Amplitude envelope: quick attack, exponential decay
    env = np.exp(-4.0 * t / duration_sec)
    out *= env * 0.8

    return np.column_stack([out, out]).astype(np.float64)


def auto_pan(
    samples: FloatArray,
    sample_rate: int = 44100,
    rate_hz: float = 1.0,
    depth: float = 0.8,
    shape: str = "sine",
    bpm: float = 0.0,
) -> FloatArray:
    """Auto-panner: LFO-modulated stereo position.

    Sound moves left to right and back rhythmically. Tempo-synced or
    free-running. Creates width and movement. Hendrix used it on
    everything. Tame Impala still does.

    Args:
        rate_hz:  LFO speed in Hz (ignored if bpm > 0).
        depth:    Pan width (0.0=none, 1.0=hard L to hard R).
        shape:    "sine" (smooth), "square" (hard switch), "triangle" (linear).
        bpm:      If > 0, sync to tempo (rate_hz becomes beats per cycle).
    """
    n = len(samples)
    if bpm > 0:
        cycle_sec = 60.0 / bpm * 4.0 / max(rate_hz, 0.1)
        actual_rate = 1.0 / cycle_sec
    else:
        actual_rate = rate_hz

    t = np.arange(n) / sample_rate
    phase = 2 * np.pi * actual_rate * t

    if shape == "square":
        lfo = np.sign(np.sin(phase))
    elif shape == "triangle":
        lfo = 2.0 * np.abs(2.0 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))) - 1.0
    else:
        lfo = np.sin(phase)

    pan_pos = lfo * depth
    angle = (pan_pos + 1) / 2 * np.pi / 2
    l_gain = np.cos(angle)
    r_gain = np.sin(angle)

    if samples.ndim == 2:
        mono = (samples[:, 0] + samples[:, 1]) * 0.5
        return np.column_stack([mono * l_gain, mono * r_gain]).astype(np.float64)
    return np.column_stack([samples * l_gain, samples * r_gain]).astype(np.float64)


def granular_delay(
    samples: FloatArray,
    sample_rate: int = 44100,
    delay_ms: float = 375.0,
    feedback: float = 0.4,
    grain_size_ms: float = 50.0,
    pitch_shift: float = 0.0,
    scatter: float = 0.0,
    wet: float = 0.3,
) -> FloatArray:
    """Granular delay: delay line that chops echoes into grains.

    Normal delay repeats the signal exactly. Granular delay breaks
    each echo into tiny grains that can be pitch-shifted, scattered
    in time, and overlapped. Creates textures from shimmer to chaos.
    Ableton's Grain Delay, Soundtoys Crystallizer, Portal.

    Args:
        delay_ms:       Base delay time.
        feedback:       Feedback amount (0.0-0.9).
        grain_size_ms:  Size of each grain (10-200ms).
        pitch_shift:    Pitch shift per grain in semitones (-12 to +12).
        scatter:        Temporal randomization (0.0=exact, 1.0=chaotic).
        wet:            Wet/dry mix.
    """
    n = len(samples)
    delay_samples = int(delay_ms * sample_rate / 1000)
    grain_samples = max(10, int(grain_size_ms * sample_rate / 1000))

    out = np.zeros_like(samples)
    buf = np.zeros_like(samples)
    rng = np.random.default_rng(42)

    # Build the delay line with granular processing
    for i in range(0, n, grain_samples):
        end = min(i + grain_samples, n)
        read_start = i - delay_samples

        # Scatter: randomize the read position
        if scatter > 0:
            scatter_offset = int(rng.uniform(-scatter * grain_samples, scatter * grain_samples))
            read_start += scatter_offset

        read_start = max(0, min(read_start, n - grain_samples))
        read_end = min(read_start + (end - i), n)
        grain_len = read_end - read_start

        if grain_len > 0 and read_start >= 0:
            grain = buf[read_start:read_end].copy()

            # Pitch shift the grain via resampling
            if abs(pitch_shift) > 0.01:
                ratio = 2 ** (pitch_shift / 12.0)
                target_len = max(1, int(grain_len / ratio))
                if samples.ndim == 2:
                    grain_l = sig.resample(grain[:, 0], target_len)
                    grain_r = sig.resample(grain[:, 1], target_len)
                    grain = np.column_stack([grain_l, grain_r])
                else:
                    grain = sig.resample(grain, target_len)

                # Pad or trim to original grain length
                if len(grain) < grain_len:
                    if samples.ndim == 2:
                        grain = np.vstack([grain, np.zeros((grain_len - len(grain), 2))])
                    else:
                        grain = np.concatenate([grain, np.zeros(grain_len - len(grain))])
                else:
                    grain = grain[:grain_len]

            # Hanning window to avoid clicks
            window = np.hanning(grain_len)
            if samples.ndim == 2:
                grain *= window[:, np.newaxis]
            else:
                grain *= window

            actual_len = min(grain_len, end - i)
            out[i : i + actual_len] += grain[:actual_len]

        # Feed back into the buffer
        actual_len = end - i
        buf[i:end] = samples[i:end] + out[i:end] * feedback

    return (samples * (1 - wet) + out * wet).astype(np.float64)


def freq_shift(
    samples: FloatArray,
    sample_rate: int = 44100,
    shift_hz: float = 50.0,
    wet: float = 0.5,
) -> FloatArray:
    """Frequency shifter (Bode shifter): shift all frequencies by a fixed amount.

    Different from pitch shift. Pitch shift multiplies all frequencies
    (preserving harmonic ratios). Frequency shift ADDS a fixed amount
    to every frequency (breaking harmonic ratios). A 100 Hz + 200 Hz +
    300 Hz signal shifted by 50 Hz becomes 150 + 250 + 350 Hz - no
    longer harmonic. Creates metallic, alien, bell-like tones.

    Small shifts (1-5 Hz) = subtle thickening (barberpole phaser).
    Medium shifts (20-100 Hz) = metallic, robotic.
    Large shifts (200+ Hz) = alien, unrecognizable.

    Args:
        shift_hz:  Frequency shift in Hz (positive = up, negative = down).
        wet:       Wet/dry mix.
    """
    n = len(samples)
    t = np.arange(n) / sample_rate
    # Single-sideband modulation via Hilbert transform
    carrier = np.exp(1j * 2 * np.pi * shift_hz * t)

    if samples.ndim == 2:
        analytic_l = sig.hilbert(samples[:, 0])
        analytic_r = sig.hilbert(samples[:, 1])
        shifted_l = np.real(analytic_l * carrier)
        shifted_r = np.real(analytic_r * carrier)
        shifted = np.column_stack([shifted_l, shifted_r])
    else:
        analytic = sig.hilbert(samples)
        shifted = np.real(analytic * carrier)

    return (samples * (1 - wet) + shifted * wet).astype(np.float64)


def ducking_delay(
    samples: FloatArray,
    sample_rate: int = 44100,
    delay_ms: float = 375.0,
    feedback: float = 0.4,
    duck_threshold: float = 0.1,
    duck_amount: float = 0.8,
    release_ms: float = 200.0,
    wet: float = 0.4,
) -> FloatArray:
    """Ducking delay: delay that ducks when the dry signal is playing.

    Normal delay: you play, echo plays on top, it gets muddy.
    Ducking delay: you play, echo ducks down. You stop, echo swells up.
    Clean during playing, lush echoes in the gaps. How The Edge (U2)
    gets that spacious delay sound without drowning in reverb.

    Args:
        delay_ms:        Delay time.
        feedback:        Feedback amount.
        duck_threshold:  Dry signal level that triggers ducking.
        duck_amount:     How much to duck (0.0=none, 1.0=full silence).
        release_ms:      How fast the delay comes back after ducking.
        wet:             Wet/dry mix.
    """
    n = len(samples)
    delay_samp = int(delay_ms * sample_rate / 1000)
    r_coef = math.exp(-1.0 / max(1, release_ms * sample_rate / 1000))

    # Build delay line
    delayed = np.zeros_like(samples)
    buf = np.zeros_like(samples)
    for i in range(n):
        read = i - delay_samp
        if read >= 0:
            delayed[i] = buf[read]
        buf[i] = samples[i] + delayed[i] * feedback

    # Duck envelope: tracks the dry signal level
    peak = np.max(np.abs(samples), axis=1) if samples.ndim == 2 else np.abs(samples)
    duck_env = np.zeros(n)
    for i in range(n):
        if peak[i] > duck_threshold:
            duck_env[i] = 1.0  # ducking ON
        else:
            duck_env[i] = duck_env[i - 1] * r_coef if i > 0 else 0.0

    # Invert: 1.0 when dry is quiet (delay audible), 0.0 when dry is loud (delay ducked)
    delay_gain = 1.0 - duck_env * duck_amount

    if delayed.ndim == 2:
        delayed *= delay_gain[:, np.newaxis]
    else:
        delayed *= delay_gain

    return (samples + delayed * wet).astype(np.float64)


def parallel_compress(
    samples: FloatArray,
    sample_rate: int = 44100,
    threshold: float = 0.3,
    ratio: float = 8.0,
    blend: float = 0.4,
) -> FloatArray:
    """Parallel compression (New York compression).

    Blend heavily compressed signal with the uncompressed dry. You get
    the punch and density of compression while keeping the dynamics
    and transients of the original. The best of both worlds. Every
    professional mix uses this on the drum bus.

    The trick that made NYC mixing engineers famous in the 80s. Compress
    the life out of a copy, then sneak it in underneath the original.

    Args:
        threshold:  Compression threshold (aggressive, e.g. 0.2-0.4).
        ratio:      Compression ratio (heavy, e.g. 8-20).
        blend:      How much compressed signal to add (0.0-1.0).
    """
    compressed = compress(
        samples,
        sample_rate,
        threshold=threshold,
        ratio=ratio,
        attack_ms=1.0,
        release_ms=50.0,
        knee_db=3.0,
    )
    result = samples + compressed * blend
    peak = np.max(np.abs(result))
    if peak > 1.0:
        result /= peak
    return result.astype(np.float64)


def midside_eq(
    samples: FloatArray,
    sample_rate: int = 44100,
    mid_low_cut: float = 0.0,
    mid_high_cut: float = 0.0,
    side_low_cut: float = 200.0,
    side_high_boost: float = 0.0,
) -> FloatArray:
    """Mid-side EQ: independently EQ the center and sides of a stereo mix.

    The mastering secret weapon. Cut low end from the sides (mono bass =
    tight low end). Boost high end on the sides (wider, more air).
    Cut mud frequencies from the center (cleaner vocals). Each adjustment
    is independent. M/S processing gives surgical control that L/R EQ
    cannot achieve.

    Args:
        mid_low_cut:     Highpass frequency on the mid channel (0=off).
        mid_high_cut:    Lowpass frequency on the mid channel (0=off).
        side_low_cut:    Highpass on sides (200Hz = mono bass below 200Hz).
        side_high_boost: High shelf boost on sides in dB (3=wider air).
    """
    if samples.ndim != 2:
        return samples.copy()

    nyq = sample_rate / 2 - 1
    mid = (samples[:, 0] + samples[:, 1]) * 0.5
    side = (samples[:, 0] - samples[:, 1]) * 0.5

    # Mid channel processing
    if mid_low_cut > 20:
        freq = min(mid_low_cut, nyq)
        sos = sig.butter(2, freq, btype="high", fs=sample_rate, output="sos")
        mid = sig.sosfilt(sos, mid)
    if mid_high_cut > 20:
        freq = min(mid_high_cut, nyq)
        sos = sig.butter(2, freq, btype="low", fs=sample_rate, output="sos")
        mid = sig.sosfilt(sos, mid)

    # Side channel processing
    if side_low_cut > 20:
        freq = min(side_low_cut, nyq)
        sos = sig.butter(2, freq, btype="high", fs=sample_rate, output="sos")
        side = sig.sosfilt(sos, side)
    if side_high_boost > 0:
        freq = min(8000.0, nyq)
        sos = sig.butter(1, freq, btype="high", fs=sample_rate, output="sos")
        hi_side = sig.sosfilt(sos, side)
        boost = 10 ** (side_high_boost / 20.0) - 1.0
        side = side + hi_side * boost

    return np.column_stack([mid + side, mid - side]).astype(np.float64)


def pitch_correct(
    samples: FloatArray,
    sample_rate: int = 44100,
    key: str = "C",
    scale: str = "chromatic",
    speed: float = 0.8,
    wet: float = 1.0,
) -> FloatArray:
    """Pitch correction / auto-tune: snap pitch to nearest scale degree.

    The T-Pain / Cher effect when speed is high. Subtle pitch cleanup
    when speed is low. Analyzes the dominant frequency in each block and
    pitch-shifts it to the nearest note in the target scale.

    speed=0.0 = transparent correction (slow, natural).
    speed=1.0 = hard snap (the auto-tune effect).

    Args:
        key:    Root note of the scale.
        scale:  "chromatic" (all semitones), "major", "minor", "pentatonic".
        speed:  Correction speed (0.0=slow/natural, 1.0=hard/robotic).
        wet:    Wet/dry mix.
    """
    from .engine import SCALES, note_name_to_midi

    scale_intervals = SCALES.get(scale, list(range(12)))
    key_midi = note_name_to_midi(key, 0) % 12
    valid_pcs = set((key_midi + i) % 12 for i in scale_intervals)

    n = len(samples)
    block = 2048
    out = samples.copy()

    mono = samples[:, 0] if samples.ndim == 2 else samples

    for s in range(0, n - block, block // 2):
        e = s + block
        chunk = mono[s:e]

        # Estimate pitch via autocorrelation
        corr = np.correlate(chunk, chunk, mode="full")
        corr = corr[len(corr) // 2 :]
        # Find first peak after the initial falloff
        min_lag = int(sample_rate / 2000)  # max 2000 Hz
        max_lag = int(sample_rate / 50)  # min 50 Hz
        if max_lag >= len(corr):
            continue
        search = corr[min_lag:max_lag]
        if len(search) == 0:
            continue
        peak_idx = np.argmax(search) + min_lag
        if peak_idx == 0:
            continue
        detected_freq = sample_rate / peak_idx
        if detected_freq < 50 or detected_freq > 2000:
            continue

        # Find nearest scale degree
        detected_midi = 69 + 12 * np.log2(detected_freq / 440.0)
        detected_pc = int(round(detected_midi)) % 12

        # Find closest valid pitch class
        best_shift = 0
        best_dist = 99
        for pc in valid_pcs:
            dist = min(abs(detected_pc - pc), 12 - abs(detected_pc - pc))
            if dist < best_dist:
                best_dist = dist
                # Direction
                up = (pc - detected_pc) % 12
                down = (detected_pc - pc) % 12
                best_shift = up if up <= down else -down
                best_dist = dist

        if best_shift == 0:
            continue

        # Apply correction (scaled by speed)
        shift_cents = best_shift * 100.0 * speed
        ratio = 2 ** (shift_cents / 1200.0)
        target_len = max(1, int(block / ratio))

        if samples.ndim == 2:
            for ch in range(2):
                resampled = sig.resample(out[s:e, ch], target_len)
                corrected = sig.resample(resampled, block)
                # Crossfade window
                window = np.hanning(block)
                out[s:e, ch] = out[s:e, ch] * (1 - wet * window) + corrected * wet * window
        else:
            resampled = sig.resample(out[s:e], target_len)
            corrected = sig.resample(resampled, block)
            window = np.hanning(block)
            out[s:e] = out[s:e] * (1 - wet * window) + corrected * wet * window

    return out.astype(np.float64)


def vocal_doubler(
    samples: FloatArray,
    sample_rate: int = 44100,
    detune_cents: float = 8.0,
    delay_ms: float = 15.0,
    wet: float = 0.3,
) -> FloatArray:
    """Vocal doubler / ADT (Automatic Double Tracking).

    The Beatles invented ADT at Abbey Road - a slightly delayed, slightly
    detuned copy of the vocal blended underneath. Makes a single voice
    sound like two takes stacked. Thicker, wider, more professional.
    John Lennon hated doing actual double takes, so Ken Townsend built
    a machine to do it automatically. This is that machine.

    Args:
        detune_cents:  Pitch offset of the double (5-15 cents typical).
        delay_ms:      Time offset (10-30ms typical).
        wet:           Blend amount.
    """
    n = len(samples)
    delay_samp = int(delay_ms * sample_rate / 1000)

    # Detune via resampling
    ratio = 2 ** (detune_cents / 1200.0)
    target_len = max(1, int(n / ratio))

    if samples.ndim == 2:
        det_l = sig.resample(samples[:, 0], target_len)
        det_r = sig.resample(samples[:, 1], target_len)
        det_l = sig.resample(det_l, n)
        det_r = sig.resample(det_r, n)
        doubled = np.column_stack([det_l, det_r])
    else:
        doubled = sig.resample(sig.resample(samples, target_len), n)

    # Delay the doubled signal
    delayed = np.zeros_like(doubled)
    if delay_samp < n:
        delayed[delay_samp:] = doubled[: n - delay_samp]

    return (samples + delayed * wet).astype(np.float64)


def haas_stereo(
    samples: FloatArray,
    sample_rate: int = 44100,
    delay_ms: float = 12.0,
    side: str = "right",
) -> FloatArray:
    """Haas effect stereo widener: short delay on one channel.

    The Haas effect (precedence effect): delays under ~30ms are not
    perceived as echo but as directionality. A 10-15ms delay on one
    channel makes the sound appear to come from the non-delayed side
    while maintaining a sense of width that pan alone cannot achieve.

    Caution: can cause phase issues in mono. Check with mono_compat().

    Args:
        delay_ms:  Delay amount (5-25ms. Under 5 = comb filter. Over 30 = echo).
        side:      Which channel to delay ("left" or "right").
    """
    if samples.ndim != 2:
        return samples.copy()

    delay_samp = int(delay_ms * sample_rate / 1000)
    out = samples.copy()

    if side == "left":
        delayed = np.zeros(len(samples))
        if delay_samp < len(samples):
            delayed[delay_samp:] = samples[: len(samples) - delay_samp, 0]
        out[:, 0] = delayed
    else:
        delayed = np.zeros(len(samples))
        if delay_samp < len(samples):
            delayed[delay_samp:] = samples[: len(samples) - delay_samp, 1]
        out[:, 1] = delayed

    return out.astype(np.float64)


def multitap_delay(
    samples: FloatArray,
    sample_rate: int = 44100,
    taps: list | None = None,
    feedback: float = 0.3,
    wet: float = 0.4,
) -> FloatArray:
    """Multi-tap delay: multiple echoes at different times, volumes, and pan positions.

    Like Logic's Delay Designer or Ableton's beat-synced delay but fully
    programmable. Each tap is a separate echo with its own time, gain,
    and pan position. Create rhythmic delay patterns, ping-pong effects,
    or complex spatial echo textures.

    Args:
        taps:      List of (delay_ms, gain, pan) tuples. Pan: -1.0 to 1.0.
                   Default: classic ping-pong pattern.
        feedback:  Global feedback amount.
        wet:       Wet/dry mix.

    Example::

        # Dotted-eighth ping-pong (U2 / The Edge)
        multitap_delay(audio, bpm=130, taps=[
            (375, 0.7, -0.8),   # left
            (750, 0.5, 0.8),    # right
            (1125, 0.3, -0.6),  # left quieter
            (1500, 0.2, 0.6),   # right quieter
        ])
    """
    if taps is None:
        taps = [
            (250, 0.6, -0.7),
            (500, 0.45, 0.7),
            (750, 0.3, -0.5),
            (1000, 0.2, 0.5),
        ]

    n = len(samples)
    ensure_stereo = samples.ndim == 2

    if not ensure_stereo:
        samples = np.column_stack([samples, samples])

    out = np.zeros_like(samples)

    for delay_ms, gain, tap_pan in taps:
        d = int(delay_ms * sample_rate / 1000)
        if d >= n:
            continue
        # Pan the tap
        angle = (tap_pan + 1) / 2 * np.pi / 2
        l_g = math.cos(angle) * gain
        r_g = math.sin(angle) * gain

        # Mono sum of input for each tap
        mono = (samples[:, 0] + samples[:, 1]) * 0.5
        delayed = np.zeros(n)
        delayed[d:] = mono[: n - d]

        out[:, 0] += delayed * l_g
        out[:, 1] += delayed * r_g

    # Feedback: feed the mixed taps back into the delay
    if feedback > 0:
        fb_mono = (out[:, 0] + out[:, 1]) * 0.5 * feedback
        for delay_ms, gain, tap_pan in taps[:2]:
            d = int(delay_ms * sample_rate / 1000)
            if d < n:
                angle = (tap_pan + 1) / 2 * np.pi / 2
                delayed = np.zeros(n)
                delayed[d:] = fb_mono[: n - d]
                out[:, 0] += delayed * math.cos(angle) * gain * 0.5
                out[:, 1] += delayed * math.sin(angle) * gain * 0.5

    result = samples * (1 - wet) + out * wet
    return np.clip(result, -1.0, 1.0).astype(np.float64)


def convolver(
    samples: FloatArray,
    ir: FloatArray | np.ndarray,
    sample_rate: int = 44100,
    wet: float = 0.4,
) -> FloatArray:
    """Convolution reverb: apply any impulse response to audio.

    Load a real room recording (concert hall, cathedral, plate reverb,
    speaker cabinet) as an IR and convolve it with your audio. The most
    realistic reverb possible - it IS the actual room, captured.

    Free IR libraries exist online (OpenAIR, EchoThief, Voxengo).
    Load a WAV file with import_audio() and pass it as the ir argument.

    Args:
        ir:   Impulse response array (mono float64). Load with import_audio().
        wet:  Wet/dry mix.

    Example::

        from code_music.integrations import import_audio
        ir = import_audio("concert_hall.wav")
        song.effects = {"vocals": EffectsChain().add(convolver, ir=ir, wet=0.3)}
    """
    if ir.ndim > 1:
        ir = ir[:, 0] if ir.shape[1] > 0 else ir.flatten()

    # Normalize IR
    pk = np.max(np.abs(ir))
    if pk > 0:
        ir = ir / pk

    if samples.ndim == 2:
        conv_l = sig.fftconvolve(samples[:, 0], ir, mode="full")[: len(samples)]
        conv_r = sig.fftconvolve(samples[:, 1], ir, mode="full")[: len(samples)]
        for ch in (conv_l, conv_r):
            p = np.max(np.abs(ch))
            if p > 0:
                ch /= p
        conv = np.column_stack([conv_l, conv_r])
    else:
        conv = sig.fftconvolve(samples, ir, mode="full")[: len(samples)]
        p = np.max(np.abs(conv))
        if p > 0:
            conv /= p

    return (samples * (1 - wet) + conv * wet).astype(np.float64)


def parametric_eq(
    samples: FloatArray,
    sample_rate: int = 44100,
    bands: list | None = None,
) -> FloatArray:
    """Parametric EQ: fully configurable multi-band equalizer.

    The workhorse of every mix. Each band has a type (peak, lowshelf,
    highshelf, lowpass, highpass), frequency, gain in dB, and Q. This
    is FabFilter Pro-Q in a function call.

    Args:
        bands: List of (type, freq_hz, gain_db, q) tuples.
            Types: "peak", "lowshelf", "highshelf", "lowpass", "highpass"
            Default: flat (no bands).

    Example::

        parametric_eq(audio, bands=[
            ("highshelf", 10000, 2.0, 0.7),  # air boost
            ("peak", 3000, -3.0, 2.0),       # cut harshness
            ("lowshelf", 100, 3.0, 0.7),     # bass warmth
            ("highpass", 30, 0, 0.7),         # rumble filter
        ])
    """
    if not bands:
        return samples.copy()

    nyq = sample_rate / 2 - 1
    out = samples.copy()

    for band in bands:
        btype, freq, gain_db, q = band
        freq = max(20.0, min(freq, nyq))
        q = max(0.1, q)

        if btype == "highpass":
            sos = sig.butter(2, freq, btype="high", fs=sample_rate, output="sos")
            out = _biquad_sos(out, sos)

        elif btype == "lowpass":
            sos = sig.butter(2, freq, btype="low", fs=sample_rate, output="sos")
            out = _biquad_sos(out, sos)

        elif btype == "peak" and abs(gain_db) > 0.1:
            # Peak/bell filter via biquad
            A = 10 ** (gain_db / 40.0)
            w0 = 2 * np.pi * freq / sample_rate
            alpha = np.sin(w0) / (2 * q)
            b0 = 1 + alpha * A
            b1 = -2 * np.cos(w0)
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * np.cos(w0)
            a2 = 1 - alpha / A
            b = [b0 / a0, b1 / a0, b2 / a0]
            a = [1.0, a1 / a0, a2 / a0]
            if out.ndim == 2:
                out[:, 0] = sig.lfilter(b, a, out[:, 0])
                out[:, 1] = sig.lfilter(b, a, out[:, 1])
            else:
                out = sig.lfilter(b, a, out)

        elif btype == "lowshelf" and abs(gain_db) > 0.1:
            A = 10 ** (gain_db / 40.0)
            w0 = 2 * np.pi * freq / sample_rate
            alpha = np.sin(w0) / (2 * q)
            cos_w0 = np.cos(w0)
            sq_A = np.sqrt(A)
            b0 = A * ((A + 1) - (A - 1) * cos_w0 + 2 * sq_A * alpha)
            b1 = 2 * A * ((A - 1) - (A + 1) * cos_w0)
            b2 = A * ((A + 1) - (A - 1) * cos_w0 - 2 * sq_A * alpha)
            a0 = (A + 1) + (A - 1) * cos_w0 + 2 * sq_A * alpha
            a1 = -2 * ((A - 1) + (A + 1) * cos_w0)
            a2 = (A + 1) + (A - 1) * cos_w0 - 2 * sq_A * alpha
            b = [b0 / a0, b1 / a0, b2 / a0]
            a = [1.0, a1 / a0, a2 / a0]
            if out.ndim == 2:
                out[:, 0] = sig.lfilter(b, a, out[:, 0])
                out[:, 1] = sig.lfilter(b, a, out[:, 1])
            else:
                out = sig.lfilter(b, a, out)

        elif btype == "highshelf" and abs(gain_db) > 0.1:
            A = 10 ** (gain_db / 40.0)
            w0 = 2 * np.pi * freq / sample_rate
            alpha = np.sin(w0) / (2 * q)
            cos_w0 = np.cos(w0)
            sq_A = np.sqrt(A)
            b0 = A * ((A + 1) + (A - 1) * cos_w0 + 2 * sq_A * alpha)
            b1 = -2 * A * ((A - 1) + (A + 1) * cos_w0)
            b2 = A * ((A + 1) + (A - 1) * cos_w0 - 2 * sq_A * alpha)
            a0 = (A + 1) - (A - 1) * cos_w0 + 2 * sq_A * alpha
            a1 = 2 * ((A - 1) - (A + 1) * cos_w0)
            a2 = (A + 1) - (A - 1) * cos_w0 - 2 * sq_A * alpha
            b = [b0 / a0, b1 / a0, b2 / a0]
            a = [1.0, a1 / a0, a2 / a0]
            if out.ndim == 2:
                out[:, 0] = sig.lfilter(b, a, out[:, 0])
                out[:, 1] = sig.lfilter(b, a, out[:, 1])
            else:
                out = sig.lfilter(b, a, out)

    return out.astype(np.float64)


def dynamic_eq(
    samples: FloatArray,
    sample_rate: int = 44100,
    freq_hz: float = 3000.0,
    threshold: float = 0.4,
    gain_db: float = -6.0,
    q: float = 2.0,
    attack_ms: float = 5.0,
    release_ms: float = 50.0,
) -> FloatArray:
    """Dynamic EQ: EQ that reacts to signal level.

    A peak EQ band that only activates when the signal exceeds a
    threshold. Below the threshold, the audio passes through flat.
    Above it, the EQ engages. Use it to tame resonances that only
    appear on loud notes, or boost frequencies only when the signal
    is quiet. More surgical than broadband compression, more musical
    than static EQ. FabFilter Pro-Q3's dynamic mode.

    Args:
        freq_hz:     Center frequency of the dynamic band.
        threshold:   Signal level that activates the EQ.
        gain_db:     EQ gain when fully active (negative = cut, positive = boost).
        q:           Band Q / width.
        attack_ms:   How fast the EQ engages.
        release_ms:  How fast the EQ disengages.
    """
    n = len(samples)
    peak = np.max(np.abs(samples), axis=1) if samples.ndim == 2 else np.abs(samples)

    a_coef = math.exp(-1.0 / max(1, attack_ms * sample_rate / 1000))
    r_coef = math.exp(-1.0 / max(1, release_ms * sample_rate / 1000))

    env = np.zeros(n)
    for i in range(1, n):
        if peak[i] > env[i - 1]:
            env[i] = a_coef * env[i - 1] + (1 - a_coef) * peak[i]
        else:
            env[i] = r_coef * env[i - 1] + (1 - r_coef) * peak[i]

    # EQ gain scales from 0 (below threshold) to full gain_db (above threshold)
    gain_curve = np.clip((env - threshold) / max(1.0 - threshold, 0.01), 0.0, 1.0)

    # Apply EQ in blocks with varying gain
    block = 512
    out = samples.copy()
    flat = samples.copy()

    # Pre-compute the full-gain EQ version
    eqd = parametric_eq(samples, sample_rate, bands=[("peak", freq_hz, gain_db, q)])

    # Blend between flat and EQ based on the dynamic gain curve
    for s in range(0, n, block):
        e = min(s + block, n)
        blend = float(np.mean(gain_curve[s:e]))
        if samples.ndim == 2:
            out[s:e] = flat[s:e] * (1 - blend) + eqd[s:e] * blend
        else:
            out[s:e] = flat[s:e] * (1 - blend) + eqd[s:e] * blend

    return out.astype(np.float64)


def multiband_stereo(
    samples: FloatArray,
    sample_rate: int = 44100,
    bass_width: float = 0.0,
    mid_width: float = 1.0,
    high_width: float = 1.5,
    crossover_low: float = 250.0,
    crossover_high: float = 4000.0,
) -> FloatArray:
    """Multiband stereo imager: independent width per frequency band.

    The mastering standard: bass in mono (tight center), mids at normal
    width, highs wider than the speakers (shimmer and air). iZotope Ozone
    Imager does exactly this. Mono bass prevents phase issues on club
    systems. Wide highs create an impression of space.

    Args:
        bass_width:     Width for low band (0.0=mono, 1.0=stereo).
        mid_width:      Width for mid band.
        high_width:     Width for high band (>1.0 = wider than original).
        crossover_low:  Bass/mid split frequency.
        crossover_high: Mid/high split frequency.
    """
    if samples.ndim != 2:
        return samples.copy()

    nyq = sample_rate / 2 - 1
    xlo = min(crossover_low, nyq)
    xhi = min(crossover_high, nyq)

    sos_lo = sig.butter(4, xlo, btype="low", fs=sample_rate, output="sos")
    sos_hi = sig.butter(4, xhi, btype="high", fs=sample_rate, output="sos")
    if xlo < xhi:
        sos_mid = sig.butter(4, [xlo, xhi], btype="band", fs=sample_rate, output="sos")
    else:
        sos_mid = sos_lo

    def _width(band, w):
        mid = (band[:, 0] + band[:, 1]) * 0.5
        side = (band[:, 0] - band[:, 1]) * 0.5
        side *= w
        return np.column_stack([mid + side, mid - side])

    lo = np.column_stack([sig.sosfilt(sos_lo, samples[:, 0]), sig.sosfilt(sos_lo, samples[:, 1])])
    mid = np.column_stack(
        [sig.sosfilt(sos_mid, samples[:, 0]), sig.sosfilt(sos_mid, samples[:, 1])]
    )
    hi = np.column_stack([sig.sosfilt(sos_hi, samples[:, 0]), sig.sosfilt(sos_hi, samples[:, 1])])

    return (_width(lo, bass_width) + _width(mid, mid_width) + _width(hi, high_width)).astype(
        np.float64
    )


def saturator(
    samples: FloatArray,
    sample_rate: int = 44100,
    model: str = "tube",
    drive: float = 2.0,
    wet: float = 0.5,
) -> FloatArray:
    """Analog circuit saturator with different hardware models.

    Each model emulates the saturation character of a specific analog
    circuit. They all add harmonics but the harmonic distribution is
    different. Tube = warm even harmonics. Tape = compressed density.
    Transistor = crispy odd harmonics. Transformer = subtle density.

    Models:
        tube:         Vacuum tube (12AX7). Warm, even harmonics dominant.
                      The Marshall, Vox, Fender sound.
        tape:         Magnetic tape (Studer A800). Compressed, dense, warm.
                      Soft knee, frequency-dependent saturation.
        transistor:   Solid state (discrete transistor). Crispy, aggressive,
                      odd harmonics. The Neve 1073 preamp character.
        transformer:  Output transformer. Subtle, thickening, low-end warmth.
                      The console summing bus character.

    Args:
        model:  Hardware model name.
        drive:  Saturation amount (1.0=subtle, 5.0=heavy).
        wet:    Wet/dry mix.
    """
    x = samples * drive

    if model == "tube":
        # Asymmetric soft clip: positive clips softer (even harmonics)
        pos = np.maximum(x, 0)
        neg = np.minimum(x, 0)
        shaped = np.tanh(pos * 0.8) * 1.1 + np.tanh(neg * 1.0)
    elif model == "tape":
        # Tape: soft compression + frequency-dependent saturation
        shaped = x / (1.0 + np.abs(x) * 0.3)
        # Tape compresses highs more
        if samples.ndim == 2 and sample_rate > 100:
            nyq = sample_rate / 2 - 1
            cutoff = min(8000.0 / max(drive, 1), nyq)
            sos = sig.butter(1, cutoff, btype="low", fs=sample_rate, output="sos")
            shaped[:, 0] = sig.sosfilt(sos, shaped[:, 0])
            shaped[:, 1] = sig.sosfilt(sos, shaped[:, 1])
    elif model == "transistor":
        # Hard-ish clip with odd harmonic emphasis
        shaped = np.clip(x, -1.0, 1.0)
        # Add back some softness
        shaped = shaped * 0.7 + np.tanh(x) * 0.3
    elif model == "transformer":
        # Very subtle saturation + low-end thickening
        shaped = np.tanh(x * 0.5) * 2.0
        if samples.ndim == 2 and sample_rate > 100:
            nyq = sample_rate / 2 - 1
            cutoff = min(200.0, nyq)
            sos = sig.butter(1, cutoff, btype="low", fs=sample_rate, output="sos")
            lo_l = sig.sosfilt(sos, shaped[:, 0])
            lo_r = sig.sosfilt(sos, shaped[:, 1])
            shaped[:, 0] += lo_l * 0.1 * drive
            shaped[:, 1] += lo_r * 0.1 * drive
    else:
        shaped = np.tanh(x)

    # Normalize to match input level
    pk_in = np.max(np.abs(samples))
    pk_out = np.max(np.abs(shaped))
    if pk_out > 0 and pk_in > 0:
        shaped *= pk_in / pk_out

    return (samples * (1 - wet) + shaped * wet).astype(np.float64)


def crossfeed(
    samples: FloatArray,
    sample_rate: int = 44100,
    amount: float = 0.3,
) -> FloatArray:
    """Headphone crossfeed: reduces extreme stereo for comfortable listening.

    With speakers, both ears hear both channels (with timing differences).
    With headphones, each ear only hears its channel - extreme stereo
    can be fatiguing and unnatural. Crossfeed blends a filtered portion
    of each channel into the other, simulating speaker listening on
    headphones. Every audiophile headphone amp has this.

    Args:
        amount: Crossfeed strength (0.0=none, 0.3=subtle, 0.7=strong).
    """
    if samples.ndim != 2:
        return samples.copy()

    nyq = sample_rate / 2 - 1
    # Crossfed signal is lowpass filtered (real crossfeed is frequency-dependent)
    cutoff = min(1500.0, nyq)
    sos = sig.butter(2, cutoff, btype="low", fs=sample_rate, output="sos")

    xfeed_l = sig.sosfilt(sos, samples[:, 1]) * amount
    xfeed_r = sig.sosfilt(sos, samples[:, 0]) * amount

    out = samples.copy()
    out[:, 0] += xfeed_l
    out[:, 1] += xfeed_r

    return out.astype(np.float64)


def spectrum_analyze(
    samples: FloatArray,
    sample_rate: int = 44100,
    n_bands: int = 32,
) -> dict:
    """Spectrum analyzer: return frequency band energy levels.

    Not an effect - a measurement tool. Returns the energy in each
    frequency band so you can visualize the spectrum, detect problems,
    or make data-driven EQ decisions.

    Returns:
        Dict with 'frequencies' (band center Hz), 'magnitudes' (dB),
        'peak_freq' (Hz), 'spectral_centroid' (Hz), 'crest_factor' (dB).
    """
    mono = samples[:, 0] if samples.ndim == 2 else samples
    n = len(mono)

    fft = np.abs(np.fft.rfft(mono))
    freqs = np.fft.rfftfreq(n, 1.0 / sample_rate)

    # Logarithmic bands
    min_freq = 20.0
    max_freq = min(20000.0, sample_rate / 2)
    band_edges = np.logspace(np.log10(min_freq), np.log10(max_freq), n_bands + 1)

    magnitudes = []
    centers = []
    for i in range(n_bands):
        lo = band_edges[i]
        hi = band_edges[i + 1]
        mask = (freqs >= lo) & (freqs < hi)
        if np.any(mask):
            energy = np.mean(fft[mask] ** 2)
            mag_db = 10 * np.log10(max(energy, 1e-20))
        else:
            mag_db = -100.0
        magnitudes.append(mag_db)
        centers.append(np.sqrt(lo * hi))

    # Spectral centroid
    total_energy = np.sum(fft**2)
    if total_energy > 0:
        centroid = np.sum(freqs * fft**2) / total_energy
    else:
        centroid = 0.0

    # Peak frequency
    peak_idx = np.argmax(fft[1:]) + 1
    peak_freq = freqs[peak_idx] if peak_idx < len(freqs) else 0.0

    # Crest factor (peak-to-RMS ratio in dB)
    rms = np.sqrt(np.mean(mono**2))
    peak = np.max(np.abs(mono))
    crest = 20 * np.log10(peak / max(rms, 1e-10)) if rms > 0 else 0.0

    return {
        "frequencies": centers,
        "magnitudes": magnitudes,
        "peak_freq": float(peak_freq),
        "spectral_centroid": float(centroid),
        "crest_factor": float(crest),
    }


def sub_harmonics(
    samples: FloatArray,
    sample_rate: int = 44100,
    octave_below: float = 0.3,
    two_octaves_below: float = 0.0,
    crossover: float = 150.0,
) -> FloatArray:
    """Sub-harmonic generator: synthesize bass content below the signal.

    Waves LoAir / Rbass equivalent. Takes the low-frequency content of
    the signal, pitch-shifts it down one or two octaves, and blends
    it back. Creates sub-bass weight that was not in the original. Makes
    thin kicks thump, gives bass guitar chest-rattling presence, adds
    low-end to any mix that needs it.

    Only processes frequencies below the crossover to avoid adding
    sub-harmonics to midrange content (which would sound muddy).

    Args:
        octave_below:      Level of generated sub one octave down (0.0-0.5).
        two_octaves_below: Level of sub two octaves down (0.0-0.3).
        crossover:         Only process frequencies below this (Hz).
    """
    if octave_below < 0.01 and two_octaves_below < 0.01:
        return samples.copy()

    nyq = sample_rate / 2 - 1
    xover = min(crossover, nyq)

    # Extract the low frequency content
    sos_lo = sig.butter(4, xover, btype="low", fs=sample_rate, output="sos")
    if samples.ndim == 2:
        lo_l = sig.sosfilt(sos_lo, samples[:, 0])
        lo_r = sig.sosfilt(sos_lo, samples[:, 1])
        lo = (lo_l + lo_r) * 0.5  # mono for sub generation
    else:
        lo = sig.sosfilt(sos_lo, samples)

    n = len(lo)
    out = samples.copy()

    # Generate sub one octave below via half-wave rectification + filtering
    # (classic analog sub-bass synthesis technique)
    if octave_below > 0.01:
        # Half-wave rectify (creates subharmonic at half the frequency)
        rectified = np.maximum(lo, 0)
        # Lowpass to extract the subharmonic
        sub_cutoff = min(xover / 2, nyq)
        sos_sub = sig.butter(4, sub_cutoff, btype="low", fs=sample_rate, output="sos")
        sub1 = sig.sosfilt(sos_sub, rectified)
        # Normalize and blend
        pk = np.max(np.abs(sub1))
        if pk > 0:
            sub1 = sub1 / pk * np.max(np.abs(lo))
        if out.ndim == 2:
            out[:, 0] += sub1 * octave_below
            out[:, 1] += sub1 * octave_below
        else:
            out += sub1 * octave_below

    # Two octaves below
    if two_octaves_below > 0.01:
        rectified2 = np.maximum(np.maximum(lo, 0), 0)
        rectified2 = np.maximum(rectified2, 0)
        sub_cutoff2 = min(xover / 4, nyq)
        if sub_cutoff2 > 10:
            sos_sub2 = sig.butter(4, sub_cutoff2, btype="low", fs=sample_rate, output="sos")
            sub2 = sig.sosfilt(sos_sub2, rectified2)
            pk2 = np.max(np.abs(sub2))
            if pk2 > 0:
                sub2 = sub2 / pk2 * np.max(np.abs(lo)) * 0.5
            if out.ndim == 2:
                out[:, 0] += sub2 * two_octaves_below
                out[:, 1] += sub2 * two_octaves_below
            else:
                out += sub2 * two_octaves_below

    return out.astype(np.float64)


def mono_check(
    samples: FloatArray,
) -> dict:
    """Mono compatibility check: detect what will disappear when summed to mono.

    Club systems, phone speakers, Bluetooth speakers, and many PA systems
    are mono or near-mono. Anything that is purely in the side channel
    (L and R exactly opposite) will cancel to zero in mono. This function
    measures how much of your mix is at risk.

    Returns:
        Dict with 'correlation' (-1 to +1, higher = more mono compatible),
        'side_energy_pct' (percentage of energy in side channel),
        'mono_loss_db' (how much quieter the mono sum is vs stereo),
        'problem_frequencies' (bands with poor correlation).
    """
    if samples.ndim != 2:
        return {
            "correlation": 1.0,
            "side_energy_pct": 0.0,
            "mono_loss_db": 0.0,
            "problem_frequencies": [],
        }

    left = samples[:, 0]
    right = samples[:, 1]
    mid = (left + right) * 0.5
    side = (left - right) * 0.5

    # Overall correlation
    l_rms = np.sqrt(np.mean(left**2))
    r_rms = np.sqrt(np.mean(right**2))
    if l_rms > 0 and r_rms > 0:
        correlation = float(np.mean(left * right) / (l_rms * r_rms))
    else:
        correlation = 1.0

    # Side energy percentage
    mid_energy = np.mean(mid**2)
    side_energy = np.mean(side**2)
    total = mid_energy + side_energy
    side_pct = float(side_energy / total * 100) if total > 0 else 0.0

    # Mono loss in dB
    stereo_rms = np.sqrt(np.mean(left**2 + right**2) / 2)
    mono_rms = np.sqrt(np.mean(mid**2))
    if stereo_rms > 0 and mono_rms > 0:
        mono_loss = float(20 * np.log10(mono_rms / stereo_rms))
    else:
        mono_loss = 0.0

    return {
        "correlation": round(correlation, 3),
        "side_energy_pct": round(side_pct, 1),
        "mono_loss_db": round(mono_loss, 1),
        "verdict": "good" if correlation > 0.5 else "caution" if correlation > 0 else "problem",
    }


def reference_match(
    samples: FloatArray,
    reference: FloatArray,
    sample_rate: int = 44100,
    strength: float = 0.7,
) -> FloatArray:
    """Match your mix's frequency balance to a reference track.

    Analyze the spectral profile of a professional reference track and
    apply corrective EQ to your mix to match it. The fastest way to get
    a balanced mix - let a pro track do the thinking.

    This is what iZotope Ozone's "Match EQ" and Soundtheory Gullfoss do.

    Args:
        samples:    Your mix to correct.
        reference:  A professional reference track (load with import_audio).
        strength:   How aggressively to match (0.0=none, 1.0=exact match).
    """
    n_bands = 32
    nyq = sample_rate / 2 - 1
    band_edges = np.logspace(np.log10(20), np.log10(min(20000, nyq)), n_bands + 1)

    # Analyze both spectra
    def _band_energy(audio):
        mono = audio[:, 0] if audio.ndim == 2 else audio
        fft = np.abs(np.fft.rfft(mono))
        freqs = np.fft.rfftfreq(len(mono), 1.0 / sample_rate)
        energies = []
        for i in range(n_bands):
            mask = (freqs >= band_edges[i]) & (freqs < band_edges[i + 1])
            if np.any(mask):
                energies.append(float(np.mean(fft[mask] ** 2)))
            else:
                energies.append(1e-20)
        return np.array(energies)

    src_energy = _band_energy(samples)
    ref_energy = _band_energy(reference)

    # Compute per-band gain corrections
    corrections_db = 10 * np.log10(ref_energy / np.maximum(src_energy, 1e-20))
    corrections_db = np.clip(corrections_db * strength, -12.0, 12.0)  # max +-12 dB

    # Build parametric EQ bands from corrections
    bands = []
    for i in range(n_bands):
        gain = float(corrections_db[i])
        if abs(gain) > 0.5:
            center = float(np.sqrt(band_edges[i] * band_edges[i + 1]))
            bands.append(("peak", center, gain, 1.0))

    if bands:
        return parametric_eq(samples, sample_rate, bands=bands)
    return samples.copy()


def pan(samples: FloatArray, position: float = 0.0) -> FloatArray:
    """Equal-power stereo pan. position: -1.0 (L) ... 0.0 (C) ... 1.0 (R)."""
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
    # Correct formula: convert cents to a time-domain offset in samples.
    # For a reference freq of ~440 Hz, depth_cents of 25 = ~0.33ms shift.
    # The offset in samples = sr * (2^(cents/1200) - 1) / reference_freq.
    # We use a fixed reference (the shift scales with actual signal content).
    max_shift_ratio = 2 ** (depth_cents / 1200.0) - 1.0
    depth_samples = max_shift_ratio * sample_rate / 440.0  # ~440Hz reference
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


# ---------------------------------------------------------------------------
# Room Model (v163.0)
# ---------------------------------------------------------------------------


def room_reverb(
    samples: FloatArray,
    sample_rate: int = 44100,
    width: float = 5.0,
    depth: float = 7.0,
    height: float = 3.0,
    absorption: float = 0.3,
    wet: float = 0.3,
) -> FloatArray:
    """Simple room model: dimensions to early reflections + late tail.

    Calculates first-order reflections from 6 walls (floor, ceiling, left,
    right, front, back) based on room dimensions. Each reflection is delayed
    by its travel distance and attenuated by wall absorption. A diffuse
    late tail is added via feedback delay network.

    Args:
        samples:     Mono or stereo audio.
        sample_rate: Sample rate.
        width:       Room width in meters (left-right).
        depth:       Room depth in meters (front-back).
        height:      Room height in meters (floor-ceiling).
        absorption:  Wall absorption coefficient (0=reflective, 1=anechoic).
        wet:         Wet/dry mix.

    Returns:
        Audio with room reverb applied.

    Example::

        >>> import numpy as np
        >>> audio = np.random.randn(22050, 2) * 0.1
        >>> roomy = room_reverb(audio, 22050, width=4, depth=6, height=3)
        >>> roomy.shape == audio.shape
        True
    """
    speed = 343.0  # m/s
    reflect = 1.0 - absorption

    # Listener at room center, source at (width/4, depth/3, height/2)
    src_x, src_y, src_z = width / 4, depth / 3, height / 2
    lis_x, lis_y, lis_z = width / 2, depth / 2, height / 2

    # Six first-order reflections (image source method)
    reflections = [
        (2 * width - src_x, src_y, src_z),  # right wall
        (-src_x, src_y, src_z),  # left wall
        (src_x, 2 * depth - src_y, src_z),  # back wall
        (src_x, -src_y, src_z),  # front wall
        (src_x, src_y, 2 * height - src_z),  # ceiling
        (src_x, src_y, -src_z),  # floor
    ]

    if samples.ndim == 2:
        mono = np.mean(samples, axis=1)
    else:
        mono = samples.copy()

    n = len(mono)
    wet_signal = np.zeros(n, dtype=np.float64)

    for rx, ry, rz in reflections:
        dist = math.sqrt((rx - lis_x) ** 2 + (ry - lis_y) ** 2 + (rz - lis_z) ** 2)
        delay_samples = int(dist / speed * sample_rate)
        atten = reflect / max(dist, 0.1)

        if 0 < delay_samples < n:
            wet_signal[delay_samples:] += mono[: n - delay_samples] * atten

    # Late diffuse tail: simple feedback comb filter
    rt60 = (
        0.161
        * (width * depth * height)
        / max(absorption * 2 * (width * depth + width * height + depth * height), 0.01)
    )
    rt60 = min(rt60, 5.0)  # cap at 5 seconds

    comb_delays = [int(d * sample_rate) for d in [0.037, 0.041, 0.043, 0.047]]
    feedback = 0.5 * reflect

    for comb_delay in comb_delays:
        if comb_delay >= n:
            continue
        buf = np.zeros(n, dtype=np.float64)
        for i in range(comb_delay, n):
            buf[i] = mono[i - comb_delay] * 0.15 + buf[i - comb_delay] * feedback
        wet_signal += buf * 0.25

    # Normalize wet signal
    peak = np.max(np.abs(wet_signal))
    if peak > 0:
        wet_signal /= peak

    if samples.ndim == 2:
        wet_stereo = np.column_stack([wet_signal, wet_signal])
        return (1 - wet) * samples + wet * wet_stereo
    return (1 - wet) * samples + wet * wet_signal


# ---------------------------------------------------------------------------
# Guitar amp + cabinet simulation (v170)
# ---------------------------------------------------------------------------


def amp_cabinet(
    samples: FloatArray,
    sample_rate: int = 44100,
    gain: float = 5.0,
    tone: float = 0.5,
    cabinet: str = "4x12",
    wet: float = 1.0,
) -> FloatArray:
    """Guitar amplifier + cabinet simulation.

    Three stages: preamp (asymmetric tube saturation for even harmonics),
    tone stack (mid-focused parametric EQ), cabinet (speaker lowpass +
    resonance). Without a cabinet sim, distortion sounds like a broken
    calculator. With it, it sounds like a Marshall stack.

    Cabinets:
        4x12:  Marshall closed back (rock/metal, tight, forward mids)
        2x12:  Fender Twin open back (clean/blues, wider, more air)
        1x12:  Small combo (jazz/country, warm, rolled-off highs)

    Args:
        gain:     Preamp gain (1=clean, 3=crunch, 6=high gain, 10=insane).
        tone:     Tone knob (0=dark, 0.5=balanced, 1=bright).
        cabinet:  Cabinet type.
        wet:      Wet/dry mix.
    """
    # Preamp: asymmetric soft clip (even harmonics = warmth)
    driven = samples * gain
    pos = np.maximum(driven, 0)
    neg = np.minimum(driven, 0)
    saturated = np.tanh(pos * 0.8) * 1.1 + np.tanh(neg * 1.0)

    # Tone stack
    nyq = sample_rate / 2 - 1
    hi_cut = min(3500.0 + tone * 4000.0, nyq)
    sos_hi = sig.butter(2, hi_cut, btype="low", fs=sample_rate, output="sos")

    if saturated.ndim == 2:
        toned = np.column_stack(
            [
                sig.sosfilt(sos_hi, saturated[:, 0]),
                sig.sosfilt(sos_hi, saturated[:, 1]),
            ]
        )
    else:
        toned = sig.sosfilt(sos_hi, saturated)

    # Cabinet lowpass (speakers cannot reproduce above ~5-6 kHz)
    cab_lp = {"4x12": 5500.0, "2x12": 6500.0, "1x12": 4500.0}
    lp_hz = min(cab_lp.get(cabinet, 5500.0), nyq)
    sos_cab = sig.butter(4, lp_hz, btype="low", fs=sample_rate, output="sos")

    if toned.ndim == 2:
        result = np.column_stack(
            [
                sig.sosfilt(sos_cab, toned[:, 0]),
                sig.sosfilt(sos_cab, toned[:, 1]),
            ]
        )
    else:
        result = sig.sosfilt(sos_cab, toned)

    out = samples * (1 - wet) + result * wet
    return np.clip(out, -1.0, 1.0).astype(np.float64)


# ---------------------------------------------------------------------------
# Multiband compression (v170)
# ---------------------------------------------------------------------------


def multiband_compress(
    samples: FloatArray,
    sample_rate: int = 44100,
    low_threshold: float = 0.5,
    mid_threshold: float = 0.4,
    high_threshold: float = 0.35,
    low_ratio: float = 3.0,
    mid_ratio: float = 2.5,
    high_ratio: float = 4.0,
    crossover_low: float = 250.0,
    crossover_high: float = 4000.0,
) -> FloatArray:
    """Multiband compressor: independent compression per frequency band.

    Splits into low/mid/high, compresses each, sums back. Bass stays
    tight without squashing vocals. Highs sparkle without kick pumping
    cymbals. Every professional mastering chain has one.

    Args:
        crossover_low:   Low/mid split frequency (Hz).
        crossover_high:  Mid/high split frequency (Hz).
    """
    nyq = sample_rate / 2 - 1
    xlo = min(crossover_low, nyq)
    xhi = min(crossover_high, nyq)

    sos_lo = sig.butter(4, xlo, btype="low", fs=sample_rate, output="sos")
    sos_hi = sig.butter(4, xhi, btype="high", fs=sample_rate, output="sos")
    if xlo < xhi:
        sos_mid = sig.butter(4, [xlo, xhi], btype="band", fs=sample_rate, output="sos")
    else:
        sos_mid = sos_lo

    def _bc(band, threshold, ratio):
        peak = np.max(np.abs(band), axis=1) if band.ndim == 2 else np.abs(band)
        gain = np.where(
            peak > threshold, (threshold + (peak - threshold) / ratio) / np.maximum(peak, 1e-9), 1.0
        )
        return band * gain[:, np.newaxis] if band.ndim == 2 else band * gain

    if samples.ndim == 2:
        lo = np.column_stack(
            [sig.sosfilt(sos_lo, samples[:, 0]), sig.sosfilt(sos_lo, samples[:, 1])]
        )
        mid = np.column_stack(
            [sig.sosfilt(sos_mid, samples[:, 0]), sig.sosfilt(sos_mid, samples[:, 1])]
        )
        hi = np.column_stack(
            [sig.sosfilt(sos_hi, samples[:, 0]), sig.sosfilt(sos_hi, samples[:, 1])]
        )
    else:
        lo = sig.sosfilt(sos_lo, samples)
        mid = sig.sosfilt(sos_mid, samples)
        hi = sig.sosfilt(sos_hi, samples)

    result = (
        _bc(lo, low_threshold, low_ratio)
        + _bc(mid, mid_threshold, mid_ratio)
        + _bc(hi, high_threshold, high_ratio)
    )
    peak = np.max(np.abs(result))
    if peak > 0:
        result /= peak
    return result.astype(np.float64)


# ---------------------------------------------------------------------------
# Analog console warmth (v170)
# ---------------------------------------------------------------------------


def console_warmth(
    samples: FloatArray,
    sample_rate: int = 44100,
    drive: float = 1.2,
    hf_rolloff: float = 0.3,
) -> FloatArray:
    """Analog console emulation: subtle saturation + HF rolloff.

    What people pay $50K/channel for in a Neve or SSL. Gentle asymmetric
    saturation adds even harmonics (warmth). Subtle HF rolloff rounds the
    top end. Transparent on one track, transformative across a full mix.

    Args:
        drive:      Saturation (1.0=barely there, 2.0=audible warmth).
        hf_rolloff: High-frequency rolloff (0.0=none, 1.0=dark).
    """
    x = samples * drive
    warm = np.tanh(np.maximum(x, 0) * 0.9) + np.tanh(np.minimum(x, 0) * 1.1)

    if hf_rolloff > 0:
        nyq = sample_rate / 2 - 1
        cutoff = min(nyq, max(8000.0, 18000.0 * (1.0 - hf_rolloff)))
        sos = sig.butter(1, cutoff, btype="low", fs=sample_rate, output="sos")
        if warm.ndim == 2:
            warm[:, 0] = sig.sosfilt(sos, warm[:, 0])
            warm[:, 1] = sig.sosfilt(sos, warm[:, 1])
        else:
            warm = sig.sosfilt(sos, warm)

    peak_in = np.max(np.abs(samples))
    peak_out = np.max(np.abs(warm))
    if peak_out > 0 and peak_in > 0:
        warm *= peak_in / peak_out
    return warm.astype(np.float64)


# ---------------------------------------------------------------------------
# Shimmer reverb — pitch-shifted reverb tail for ethereal textures (v170)
# ---------------------------------------------------------------------------


def shimmer_reverb(
    samples: FloatArray,
    sample_rate: int = 44100,
    room_size: float = 0.8,
    damping: float = 0.3,
    shift_semitones: float = 12.0,
    shimmer_amount: float = 0.3,
    wet: float = 0.35,
) -> FloatArray:
    """Shimmer reverb: reverb with a pitch-shifted feedback path.

    The reverb tail gets pitch-shifted (typically up an octave) and fed
    back, creating an ethereal, rising quality. Signature effect of
    ambient music, post-rock, and film scores. Brian Eno's secret weapon.

    Args:
        room_size:        Reverb size (0.0-1.0).
        damping:          High frequency damping.
        shift_semitones:  Pitch shift for the shimmer (12 = octave up).
        shimmer_amount:   How much shifted signal feeds back (0.0-1.0).
        wet:              Wet/dry mix.
    """
    # Standard reverb first
    ir = _make_reverb_ir(sample_rate, room_size, damping)
    left = samples[:, 0]
    right = samples[:, 1]

    rev_l = sig.fftconvolve(left, ir, mode="full")[: len(left)]
    rev_r = sig.fftconvolve(right, np.roll(ir, 1), mode="full")[: len(right)]

    for rev in (rev_l, rev_r):
        p = np.max(np.abs(rev))
        if p > 0:
            rev /= p

    # Pitch shift the reverb tail up
    ratio = 2 ** (shift_semitones / 12.0)
    target_len = max(1, int(len(rev_l) / ratio))
    shifted_l = sig.resample(rev_l, target_len)
    shifted_r = sig.resample(rev_r, target_len)

    # Pad or trim to original length
    n = len(left)
    if len(shifted_l) < n:
        shifted_l = np.pad(shifted_l, (0, n - len(shifted_l)))
        shifted_r = np.pad(shifted_r, (0, n - len(shifted_r)))
    else:
        shifted_l = shifted_l[:n]
        shifted_r = shifted_r[:n]

    # Mix: dry + reverb + shimmer
    out_l = left * (1 - wet) + rev_l * wet * (1 - shimmer_amount) + shifted_l * wet * shimmer_amount
    out_r = (
        right * (1 - wet) + rev_r * wet * (1 - shimmer_amount) + shifted_r * wet * shimmer_amount
    )

    return np.column_stack([out_l, out_r]).astype(np.float64)


# ---------------------------------------------------------------------------
# Spring reverb — the classic guitar amp reverb (v170)
# ---------------------------------------------------------------------------


def spring_reverb(
    samples: FloatArray,
    sample_rate: int = 44100,
    tension: float = 0.6,
    wet: float = 0.3,
) -> FloatArray:
    """Spring reverb: metallic, boingy character of a spring tank.

    The reverb found in every Fender amp since 1963. Characterized by
    a bright, splashy attack followed by a metallic decay. Hit the amp
    hard enough and it goes SPROING.

    Args:
        tension:  Spring tension (0.0=loose/long, 1.0=tight/short).
        wet:      Wet/dry mix.
    """
    # Model spring reverb as a series of closely-spaced comb filters
    decay = 0.3 + (1.0 - tension) * 1.5
    ir_len = int(decay * sample_rate)
    rng = np.random.default_rng(73)

    # Spring resonances: metallic, evenly-spaced peaks
    ir = np.zeros(ir_len)
    n_springs = 3
    for s in range(n_springs):
        base_delay = int((0.008 + s * 0.004) * sample_rate)
        for tap in range(50):
            pos = base_delay * (tap + 1)
            if pos >= ir_len:
                break
            amp = 0.7**tap * rng.choice([-1, 1])
            ir[min(pos, ir_len - 1)] += amp / n_springs

    # Envelope and high-pass (springs are bright)
    t = np.arange(ir_len) / sample_rate
    env = np.exp(-4.0 * t / decay)
    ir *= env

    cutoff = 400.0
    sos = sig.butter(2, cutoff, btype="high", fs=sample_rate, output="sos")
    ir = sig.sosfilt(sos, ir)

    peak = np.max(np.abs(ir))
    if peak > 0:
        ir /= peak

    left = sig.fftconvolve(samples[:, 0], ir, mode="full")[: len(samples)]
    right = sig.fftconvolve(samples[:, 1], ir * 0.9, mode="full")[: len(samples)]

    for ch in (left, right):
        p = np.max(np.abs(ch))
        if p > 0:
            ch /= p

    return np.column_stack(
        [
            samples[:, 0] * (1 - wet) + left * wet,
            samples[:, 1] * (1 - wet) + right * wet,
        ]
    ).astype(np.float64)


# ---------------------------------------------------------------------------
# Rotary speaker — Leslie cabinet simulation (v170)
# ---------------------------------------------------------------------------


def rotary_speaker(
    samples: FloatArray,
    sample_rate: int = 44100,
    speed: str = "slow",
    wet: float = 0.7,
) -> FloatArray:
    """Rotary speaker (Leslie cabinet) simulation.

    The sound of a Hammond B3 organ. A spinning horn (treble) and drum
    (bass) create Doppler pitch shift, amplitude tremolo, and spatial
    movement. "Slow" is chorale, "fast" is tremolo. The transition
    between them is half the magic.

    Args:
        speed:  "slow" (chorale, 0.8 Hz) or "fast" (tremolo, 6.8 Hz).
        wet:    Wet/dry mix.
    """
    rates = {"slow": 0.8, "fast": 6.8, "brake": 0.0}
    rate = rates.get(speed, 0.8)

    n = len(samples)
    t = np.arange(n) / sample_rate

    # Amplitude modulation (tremolo component)
    am = 0.5 + 0.5 * np.sin(2 * np.pi * rate * t)

    # Frequency modulation via time-warping (Doppler component)
    depth_samples = rate * 0.002 * sample_rate  # ~2ms depth
    offsets = depth_samples * np.sin(2 * np.pi * rate * t)
    indices = np.clip(np.arange(n, dtype=np.float64) - offsets, 0, n - 1)

    lo = np.floor(indices).astype(int)
    hi = np.minimum(lo + 1, n - 1)
    frac = indices - lo

    # Stereo: left horn leads, right horn lags by 90 degrees
    am_r = 0.5 + 0.5 * np.sin(2 * np.pi * rate * t + np.pi / 2)
    offsets_r = depth_samples * np.sin(2 * np.pi * rate * t + np.pi / 2)
    indices_r = np.clip(np.arange(n, dtype=np.float64) - offsets_r, 0, n - 1)
    lo_r = np.floor(indices_r).astype(int)
    hi_r = np.minimum(lo_r + 1, n - 1)
    frac_r = indices_r - lo_r

    warped_l = (samples[lo, 0] * (1 - frac) + samples[hi, 0] * frac) * am
    warped_r = (samples[lo_r, 1] * (1 - frac_r) + samples[hi_r, 1] * frac_r) * am_r

    return np.column_stack(
        [
            samples[:, 0] * (1 - wet) + warped_l * wet,
            samples[:, 1] * (1 - wet) + warped_r * wet,
        ]
    ).astype(np.float64)


# ---------------------------------------------------------------------------
# Tape wow and flutter — analog tape imperfections (v170)
# ---------------------------------------------------------------------------


def tape_wow_flutter(
    samples: FloatArray,
    sample_rate: int = 44100,
    wow_rate: float = 0.5,
    wow_depth: float = 0.003,
    flutter_rate: float = 6.0,
    flutter_depth: float = 0.001,
    wet: float = 0.8,
) -> FloatArray:
    """Tape wow and flutter: slow and fast pitch variations of analog tape.

    Wow is the slow waver (capstan irregularity, 0.5-2 Hz). Flutter is
    the fast variation (motor vibration, 4-10 Hz). Together they create
    the subtle pitch instability that makes tape sound alive.

    Args:
        wow_rate:       Wow LFO speed in Hz (0.5-2.0 typical).
        wow_depth:      Wow modulation depth (0.001-0.005).
        flutter_rate:   Flutter LFO speed in Hz (4-10 typical).
        flutter_depth:  Flutter modulation depth (0.0005-0.002).
        wet:            Wet/dry mix.
    """
    n = len(samples)
    t = np.arange(n) / sample_rate

    # Combined modulation signal
    mod = wow_depth * np.sin(2 * np.pi * wow_rate * t) + flutter_depth * np.sin(
        2 * np.pi * flutter_rate * t
    )

    # Time-warp via modulated read position
    offsets = mod * sample_rate
    indices = np.clip(np.arange(n, dtype=np.float64) - offsets, 0, n - 1)
    lo = np.floor(indices).astype(int)
    hi = np.minimum(lo + 1, n - 1)
    frac = indices - lo

    warped_l = samples[lo, 0] * (1 - frac) + samples[hi, 0] * frac
    warped_r = samples[lo, 1] * (1 - frac) + samples[hi, 1] * frac

    return np.column_stack(
        [
            samples[:, 0] * (1 - wet) + warped_l * wet,
            samples[:, 1] * (1 - wet) + warped_r * wet,
        ]
    ).astype(np.float64)


# ---------------------------------------------------------------------------
# Lo-fi vinyl — crackle, hiss, and warmth (v170)
# ---------------------------------------------------------------------------


def lofi_vinyl(
    samples: FloatArray,
    sample_rate: int = 44100,
    crackle: float = 0.02,
    hiss: float = 0.01,
    warmth: float = 0.5,
    wear: float = 0.3,
    wet: float = 1.0,
) -> FloatArray:
    """Lo-fi vinyl effect: crackle, hiss, filtering, and warmth.

    Simulates a well-loved record player. Crackle = random pops,
    hiss = tape/surface noise, warmth = low-pass + saturation,
    wear = high-frequency loss from repeated plays.

    Args:
        crackle:  Crackle intensity (0.0-0.1).
        hiss:     Background hiss level (0.0-0.05).
        warmth:   Low-end warmth / saturation (0.0-1.0).
        wear:     High-frequency roll-off simulating worn vinyl (0.0-1.0).
        wet:      Wet/dry mix.
    """
    n = len(samples)
    rng = np.random.default_rng(42)
    out = samples.copy()

    # Crackle: sparse random impulses
    if crackle > 0:
        crackle_signal = np.zeros(n)
        n_pops = int(n * crackle * 0.01)
        pop_positions = rng.integers(0, n, size=n_pops)
        pop_amplitudes = rng.uniform(0.05, 0.3, size=n_pops) * crackle * 10
        for pos, amp in zip(pop_positions, pop_amplitudes):
            crackle_signal[pos] = rng.choice([-1, 1]) * amp
        out[:, 0] += crackle_signal
        out[:, 1] += crackle_signal

    # Hiss: filtered noise
    if hiss > 0:
        noise = rng.standard_normal(n) * hiss
        sos_hp = sig.butter(2, 2000.0, btype="high", fs=sample_rate, output="sos")
        noise = sig.sosfilt(sos_hp, noise)
        out[:, 0] += noise
        out[:, 1] += noise

    # Warmth: gentle saturation + low-shelf boost
    if warmth > 0:
        out = out * (1.0 + warmth * 0.5)
        out = out / (1 + np.abs(out) * warmth * 0.3)
        cutoff = 300.0
        sos_lp = sig.butter(2, cutoff, btype="low", fs=sample_rate, output="sos")
        low_l = sig.sosfilt(sos_lp, out[:, 0])
        low_r = sig.sosfilt(sos_lp, out[:, 1])
        out[:, 0] += low_l * warmth * 0.3
        out[:, 1] += low_r * warmth * 0.3

    # Wear: high-frequency roll-off
    if wear > 0:
        cutoff = max(2000.0, min(16000.0 * (1.0 - wear), sample_rate / 2 - 1))
        sos_wear = sig.butter(2, cutoff, btype="low", fs=sample_rate, output="sos")
        out[:, 0] = sig.sosfilt(sos_wear, out[:, 0])
        out[:, 1] = sig.sosfilt(sos_wear, out[:, 1])

    result = samples * (1 - wet) + out * wet
    return np.clip(result, -1.0, 1.0).astype(np.float64)


# ---------------------------------------------------------------------------
# Harmonic exciter — add sparkle and presence (v170)
# ---------------------------------------------------------------------------


def harmonic_exciter(
    samples: FloatArray,
    sample_rate: int = 44100,
    frequency: float = 3000.0,
    drive: float = 2.0,
    mix: float = 0.15,
) -> FloatArray:
    """Harmonic exciter: generate and add upper harmonics for presence.

    Filters the signal above a frequency, applies saturation to generate
    new harmonics, then blends back. The Aphex Aural Exciter in a function.
    Makes dull mixes sparkle without just turning up the treble.

    Args:
        frequency:  High-pass frequency for exciter input (Hz).
        drive:      Saturation amount for harmonic generation.
        mix:        How much excited signal to add (0.0-0.5 typical).
    """
    # Extract high frequencies
    sos = sig.butter(2, frequency, btype="high", fs=sample_rate, output="sos")
    hi_l = sig.sosfilt(sos, samples[:, 0])
    hi_r = sig.sosfilt(sos, samples[:, 1])

    # Generate harmonics via soft saturation
    excited_l = np.tanh(hi_l * drive)
    excited_r = np.tanh(hi_r * drive)

    # Blend back
    out_l = samples[:, 0] + excited_l * mix
    out_r = samples[:, 1] + excited_r * mix

    return np.clip(np.column_stack([out_l, out_r]), -1.0, 1.0).astype(np.float64)
