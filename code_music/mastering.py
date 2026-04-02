"""Production mastering pipeline — LUFS metering, true peak limiting, dithering.

Bridge the gap from demo to release-ready audio. All functions operate on
stereo float64 arrays (shape N×2) and return the same.

Example::

    from code_music.mastering import measure_lufs, normalize_lufs, true_peak_limit, dither

    audio = song.render()
    lufs = measure_lufs(audio, 44100)
    audio = normalize_lufs(audio, 44100, target_lufs=-14.0)
    audio = true_peak_limit(audio, 44100, ceiling_db=-1.0)
    audio = dither(audio, bit_depth=16)
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


# ---------------------------------------------------------------------------
# LUFS Loudness Metering (ITU-R BS.1770-4 simplified)
# ---------------------------------------------------------------------------


def _k_weight_filter(audio: FloatArray, sr: int) -> FloatArray:
    """Apply K-weighting filter (simplified two-stage shelving).

    Stage 1: pre-filter (high shelf +4dB at ~1500Hz)
    Stage 2: RLB weighting (highpass ~38Hz)

    This is a simplified implementation that captures the essential
    frequency weighting without requiring scipy.
    """
    # Stage 1: High shelf boost (~+4dB above 1500Hz)
    # Simple first-order shelf approximation
    fc = 1500.0
    gain = 10 ** (4.0 / 20.0)  # +4dB
    wc = 2 * np.pi * fc / sr
    alpha = (1 - np.sin(wc)) / np.cos(wc) if np.cos(wc) != 0 else 0.0

    filtered = np.copy(audio)
    for ch in range(audio.shape[1] if audio.ndim > 1 else 1):
        col = audio[:, ch] if audio.ndim > 1 else audio
        out = np.zeros_like(col)
        x1 = 0.0
        y1 = 0.0
        a0 = (gain + 1) + (gain - 1) * alpha
        b0_coeff = gain * ((gain + 1) - (gain - 1) * alpha) / a0 if a0 != 0 else 1.0
        b1_coeff = gain * ((gain - 1) - (gain + 1) * alpha) / a0 if a0 != 0 else 0.0
        a1_coeff = -((gain - 1) + (gain + 1) * alpha) / a0 if a0 != 0 else 0.0
        for i in range(len(col)):
            out[i] = b0_coeff * col[i] + b1_coeff * x1 - a1_coeff * y1
            x1 = col[i]
            y1 = out[i]
        if audio.ndim > 1:
            filtered[:, ch] = out
        else:
            filtered = out

    # Stage 2: Highpass ~38Hz (remove DC and sub-bass)
    fc2 = 38.0
    rc = 1.0 / (2 * np.pi * fc2)
    dt = 1.0 / sr
    alpha2 = rc / (rc + dt)
    for ch in range(filtered.shape[1] if filtered.ndim > 1 else 1):
        col = filtered[:, ch] if filtered.ndim > 1 else filtered
        out = np.zeros_like(col)
        out[0] = col[0]
        for i in range(1, len(col)):
            out[i] = alpha2 * (out[i - 1] + col[i] - col[i - 1])
        if filtered.ndim > 1:
            filtered[:, ch] = out
        else:
            filtered = out

    return filtered


def measure_lufs(audio: FloatArray, sr: int) -> float:
    """Measure integrated loudness in LUFS (ITU-R BS.1770-4 simplified).

    Args:
        audio: Stereo float64 array (N, 2).
        sr:    Sample rate.

    Returns:
        Integrated loudness in LUFS (typically -30 to 0).
    """
    if audio.ndim == 1:
        audio = np.column_stack([audio, audio])

    filtered = _k_weight_filter(audio, sr)

    # Mean square per channel, then sum (equal weighting for L/R)
    ms_l = np.mean(filtered[:, 0] ** 2)
    ms_r = np.mean(filtered[:, 1] ** 2)
    ms_sum = ms_l + ms_r

    if ms_sum <= 0:
        return -70.0  # silence

    lufs = -0.691 + 10 * np.log10(ms_sum)
    return float(lufs)


def normalize_lufs(audio: FloatArray, sr: int, target_lufs: float = -14.0) -> FloatArray:
    """Normalize audio to a target LUFS level.

    Args:
        audio:       Stereo float64 array (N, 2).
        sr:          Sample rate.
        target_lufs: Target integrated loudness (default -14 for streaming).

    Returns:
        Level-adjusted audio (may exceed ±1.0 — apply limiter after).
    """
    current = measure_lufs(audio, sr)
    if current <= -70.0:
        return audio  # silence, nothing to normalize

    diff_db = target_lufs - current
    gain = 10 ** (diff_db / 20.0)
    return audio * gain


# ---------------------------------------------------------------------------
# True Peak Limiting (intersample peak detection)
# ---------------------------------------------------------------------------


def true_peak_limit(
    audio: FloatArray, sr: int, ceiling_db: float = -1.0, release_ms: float = 50.0
) -> FloatArray:
    """True peak limiter with intersample peak detection.

    Upsamples 4× to catch intersample peaks, then applies gain reduction
    to keep the signal below the ceiling.

    Args:
        audio:      Stereo float64 array (N, 2).
        sr:         Sample rate.
        ceiling_db: Maximum true peak level in dBFS (default -1.0).
        release_ms: Limiter release time in ms.

    Returns:
        Peak-limited audio.
    """
    ceiling = 10 ** (ceiling_db / 20.0)

    if audio.ndim == 1:
        audio = np.column_stack([audio, audio])

    result = np.copy(audio)
    n = len(audio)

    # 4× oversampling for true peak detection (linear interpolation)
    # Process per-channel, find the max peak across both channels per sample
    oversample = 4
    for ch in range(2):
        col = audio[:, ch]
        # Simple linear interpolation for 4× oversampling
        x_orig = np.arange(n)
        x_up = np.linspace(0, n - 1, n * oversample)
        upsampled = np.interp(x_up, x_orig, col)
        # Find peaks in upsampled domain that exceed ceiling
        peaks = np.abs(upsampled)
        # Map back to original sample positions
        for i in range(n):
            region = peaks[i * oversample : (i + 1) * oversample]
            max_peak = np.max(region)
            if max_peak > ceiling:
                gain = ceiling / max_peak
                result[i, ch] = audio[i, ch] * gain

    # Smooth the gain changes to avoid clicks
    release_samples = max(1, int(release_ms * sr / 1000))
    for ch in range(2):
        gain_curve = np.where(
            np.abs(audio[:, ch]) > 0,
            np.abs(result[:, ch]) / (np.abs(audio[:, ch]) + 1e-10),
            1.0,
        )
        # Smooth with simple exponential release
        for i in range(1, n):
            if gain_curve[i] > gain_curve[i - 1]:
                alpha = 1.0 - np.exp(-2.2 / release_samples)
                gain_curve[i] = gain_curve[i - 1] + alpha * (gain_curve[i] - gain_curve[i - 1])
        result[:, ch] = audio[:, ch] * gain_curve

    return result


# ---------------------------------------------------------------------------
# Dithering (TPDF)
# ---------------------------------------------------------------------------


def dither(audio: FloatArray, bit_depth: int = 16, seed: int | None = None) -> FloatArray:
    """Apply TPDF (triangular probability density function) dithering.

    Adds shaped noise before quantization to reduce distortion when
    converting from high-resolution float to lower bit depths.

    Args:
        audio:     Float64 audio array.
        bit_depth: Target bit depth (16 or 24).
        seed:      Random seed for reproducibility.

    Returns:
        Dithered audio (still float64, ready for int conversion).
    """
    rng = np.random.default_rng(seed)
    levels = 2 ** (bit_depth - 1)
    # TPDF: sum of two uniform random variables
    noise1 = rng.uniform(-0.5, 0.5, audio.shape)
    noise2 = rng.uniform(-0.5, 0.5, audio.shape)
    tpdf_noise = (noise1 + noise2) / levels
    return audio + tpdf_noise


# ---------------------------------------------------------------------------
# Stereo imaging analysis
# ---------------------------------------------------------------------------


def stereo_analysis(audio: FloatArray) -> dict:
    """Analyze stereo image properties.

    Args:
        audio: Stereo float64 array (N, 2).

    Returns:
        Dict with correlation, width, balance, and mid/side levels.
    """
    if audio.ndim == 1:
        return {
            "correlation": 1.0,
            "width": 0.0,
            "balance": 0.0,
            "mid_rms": float(np.sqrt(np.mean(audio**2))),
            "side_rms": 0.0,
        }

    left = audio[:, 0]
    right = audio[:, 1]
    mid = (left + right) / 2.0
    side = (left - right) / 2.0

    # Stereo correlation (-1 = out of phase, 0 = uncorrelated, 1 = mono)
    l_rms = np.sqrt(np.mean(left**2))
    r_rms = np.sqrt(np.mean(right**2))
    if l_rms > 0 and r_rms > 0:
        correlation = float(np.mean(left * right) / (l_rms * r_rms))
    else:
        correlation = 1.0

    # Stereo width (0 = mono, 1 = wide)
    mid_rms = float(np.sqrt(np.mean(mid**2)))
    side_rms = float(np.sqrt(np.mean(side**2)))
    width = float(side_rms / (mid_rms + 1e-10)) if mid_rms > 0 else 0.0

    # Balance (-1 = left, 0 = center, 1 = right)
    balance = float((r_rms - l_rms) / (r_rms + l_rms + 1e-10))

    return {
        "correlation": round(correlation, 4),
        "width": round(min(width, 2.0), 4),
        "balance": round(balance, 4),
        "mid_rms": round(mid_rms, 4),
        "side_rms": round(side_rms, 4),
    }


# ---------------------------------------------------------------------------
# Master chain (combines everything)
# ---------------------------------------------------------------------------


def master_audio(
    audio: FloatArray,
    sr: int,
    target_lufs: float = -14.0,
    ceiling_db: float = -1.0,
    dither_bits: int = 16,
    dither_seed: int | None = None,
) -> FloatArray:
    """Full mastering chain: normalize LUFS → true peak limit → dither.

    Args:
        audio:       Stereo float64 (N, 2).
        sr:          Sample rate.
        target_lufs: Target loudness for streaming (-14 LUFS default).
        ceiling_db:  True peak ceiling (-1.0 dBFS default).
        dither_bits: Dithering bit depth (16 or 24).
        dither_seed: Random seed for reproducible dithering.

    Returns:
        Mastered audio ready for export.
    """
    # Step 1: Normalize to target LUFS
    audio = normalize_lufs(audio, sr, target_lufs)

    # Step 2: True peak limiting
    audio = true_peak_limit(audio, sr, ceiling_db)

    # Step 3: Dithering
    audio = dither(audio, dither_bits, dither_seed)

    # Final clip
    return np.clip(audio, -1.0, 1.0)
