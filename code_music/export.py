"""Export rendered audio to WAV, MP3, OGG, or FLAC.

Named quality presets for every major platform::

    from code_music.export import export_with_preset, QUALITY_PRESETS

    export_with_preset(audio, "my_song", "spotify-hifi", sr=44100)
    export_with_preset(audio, "my_song", "apple-lossless", sr=44100)
    export_with_preset(audio, "my_song", "archive-master", sr=44100)

Presets handle format, bit depth, sample rate, and codec settings.

Requires:
    WAV:  stdlib wave module (always available)
    MP3:  pydub + ffmpeg on PATH
    OGG:  pydub + ffmpeg on PATH
    FLAC: pydub + ffmpeg on PATH (lossless, preferred for mastering)
"""

from __future__ import annotations

import io
import struct
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


# ---------------------------------------------------------------------------
# Quality presets for every major platform
# ---------------------------------------------------------------------------


@dataclass
class QualityPreset:
    """Export settings for a target platform or use case."""

    name: str
    format: str  # wav, flac, mp3, ogg
    bit_depth: int  # 16, 24, 32 (32 = float)
    sample_rate: int  # target sample rate (source will be resampled if different)
    bitrate: str | None  # for lossy formats
    description: str


QUALITY_PRESETS: dict[str, QualityPreset] = {
    # ── Streaming platforms ──────────────────────────────────────────
    "spotify-free": QualityPreset(
        "spotify-free",
        "ogg",
        16,
        44100,
        None,
        "Spotify Free tier: OGG Vorbis ~128kbps, 16-bit/44.1kHz",
    ),
    "spotify-premium": QualityPreset(
        "spotify-premium",
        "ogg",
        16,
        44100,
        None,
        "Spotify Premium: OGG Vorbis ~320kbps, 16-bit/44.1kHz",
    ),
    "spotify-hifi": QualityPreset(
        "spotify-hifi",
        "flac",
        16,
        44100,
        None,
        "Spotify HiFi (lossless): FLAC 16-bit/44.1kHz (CD quality)",
    ),
    "spotify-upload": QualityPreset(
        "spotify-upload",
        "flac",
        24,
        44100,
        None,
        "Spotify for Artists upload: FLAC 24-bit/44.1kHz (best accepted)",
    ),
    "apple-music": QualityPreset(
        "apple-music",
        "flac",
        16,
        44100,
        None,
        "Apple Music AAC 256kbps equivalent source: FLAC 16-bit/44.1kHz",
    ),
    "apple-lossless": QualityPreset(
        "apple-lossless",
        "flac",
        24,
        48000,
        None,
        "Apple Music Lossless: FLAC 24-bit/48kHz (Apple Digital Masters)",
    ),
    "apple-hires": QualityPreset(
        "apple-hires",
        "flac",
        24,
        96000,
        None,
        "Apple Music Hi-Res Lossless: FLAC 24-bit/96kHz",
    ),
    "youtube": QualityPreset(
        "youtube",
        "flac",
        24,
        48000,
        None,
        "YouTube (upload): FLAC 24-bit/48kHz (transcoded to AAC 256kbps)",
    ),
    "tidal-hifi": QualityPreset(
        "tidal-hifi",
        "flac",
        16,
        44100,
        None,
        "Tidal HiFi: FLAC 16-bit/44.1kHz (CD quality)",
    ),
    "tidal-master": QualityPreset(
        "tidal-master",
        "flac",
        24,
        96000,
        None,
        "Tidal Master (MQA source): FLAC 24-bit/96kHz",
    ),
    "bandcamp": QualityPreset(
        "bandcamp",
        "flac",
        24,
        44100,
        None,
        "Bandcamp upload: FLAC 24-bit/44.1kHz (fans get all formats)",
    ),
    "soundcloud": QualityPreset(
        "soundcloud",
        "flac",
        24,
        44100,
        None,
        "SoundCloud upload: FLAC 24-bit/44.1kHz (transcoded to 128kbps MP3)",
    ),
    "amazon-hd": QualityPreset(
        "amazon-hd",
        "flac",
        24,
        48000,
        None,
        "Amazon Music HD: FLAC 24-bit/48kHz",
    ),
    "amazon-ultra": QualityPreset(
        "amazon-ultra",
        "flac",
        24,
        96000,
        None,
        "Amazon Music Ultra HD: FLAC 24-bit/96kHz",
    ),
    # ── Production / archival ────────────────────────────────────────
    "cd": QualityPreset(
        "cd",
        "wav",
        16,
        44100,
        None,
        "Red Book CD: WAV 16-bit/44.1kHz (the original standard)",
    ),
    "studio": QualityPreset(
        "studio",
        "wav",
        24,
        48000,
        None,
        "Studio master: WAV 24-bit/48kHz (broadcast/film standard)",
    ),
    "daw-float": QualityPreset(
        "daw-float",
        "wav",
        32,
        48000,
        None,
        "DAW interchange: WAV 32-bit float/48kHz (no dithering, full precision)",
    ),
    "archive-master": QualityPreset(
        "archive-master",
        "wav",
        32,
        96000,
        None,
        "Archival master: WAV 32-bit float/96kHz (maximum possible quality)",
    ),
    "hires": QualityPreset(
        "hires",
        "flac",
        24,
        96000,
        None,
        "Hi-Res Audio: FLAC 24-bit/96kHz (audiophile standard)",
    ),
    # ── Lossy (for specific needs) ───────────────────────────────────
    "mp3-320": QualityPreset(
        "mp3-320",
        "mp3",
        16,
        44100,
        "320k",
        "MP3 320kbps CBR: maximum MP3 quality, universally compatible",
    ),
    "mp3-v0": QualityPreset(
        "mp3-v0",
        "mp3",
        16,
        44100,
        "256k",
        "MP3 V0 (~245kbps VBR): transparent quality, smaller files",
    ),
    "podcast": QualityPreset(
        "podcast",
        "mp3",
        16,
        44100,
        "128k",
        "Podcast: MP3 128kbps mono-compatible (voice optimized)",
    ),
}


def list_quality_presets() -> list[dict[str, str]]:
    """Return all quality presets with descriptions."""
    return [
        {
            "name": p.name,
            "format": p.format,
            "bit_depth": str(p.bit_depth),
            "sample_rate": str(p.sample_rate),
            "description": p.description,
        }
        for p in QUALITY_PRESETS.values()
    ]


def export_with_preset(
    samples: FloatArray,
    path: str | Path,
    preset_name: str,
    sample_rate: int = 44100,
    metadata: dict[str, str] | None = None,
) -> Path:
    """Export audio using a named quality preset.

    Handles format selection, bit depth, sample rate conversion, and
    codec settings automatically. One flag, correct output.

    Args:
        samples:      Stereo float64 array.
        path:         Output path (extension will be set by preset).
        preset_name:  Key from QUALITY_PRESETS.
        sample_rate:  Source sample rate (will resample if preset differs).
        metadata:     Optional tags.

    Returns:
        Path of the written file.
    """
    if preset_name not in QUALITY_PRESETS:
        raise ValueError(
            f"Unknown preset {preset_name!r}. Available: {', '.join(sorted(QUALITY_PRESETS))}"
        )
    preset = QUALITY_PRESETS[preset_name]

    # Resample if needed (source rate != target rate)
    if sample_rate != preset.sample_rate:
        from scipy import signal as _sig

        target_len = int(len(samples) * preset.sample_rate / sample_rate)
        resampled_l = _sig.resample(samples[:, 0], target_len)
        resampled_r = _sig.resample(samples[:, 1], target_len)
        samples = np.column_stack([resampled_l, resampled_r])
        sample_rate = preset.sample_rate

    if preset.format == "wav":
        return export_wav(samples, path, sample_rate, bit_depth=preset.bit_depth)
    elif preset.format == "flac":
        return export_flac(
            samples, path, sample_rate, bit_depth=preset.bit_depth, metadata=metadata
        )
    elif preset.format == "mp3":
        return export_mp3(
            samples, path, sample_rate, bitrate=preset.bitrate or "320k", metadata=metadata
        )
    elif preset.format == "ogg":
        return export_ogg(samples, path, sample_rate, metadata=metadata)
    else:
        raise ValueError(f"Unsupported format: {preset.format}")


def _tpdf_dither(samples: FloatArray, bit_depth: int = 24) -> FloatArray:
    """Apply TPDF (Triangular Probability Density Function) dithering.

    Dithering adds a tiny amount of shaped noise before quantization.
    This converts the harsh quantization distortion (correlated with the
    signal) into uncorrelated noise floor (which sounds natural). TPDF
    is the standard for professional audio - it completely linearizes
    the quantization error.

    Without dithering, quiet passages in 16-bit audio have audible
    stepping artifacts. With TPDF dithering, they fade smoothly into
    a noise floor that is inaudible at normal listening levels.
    """
    quant_step = 2.0 / (2**bit_depth)
    rng = np.random.default_rng(42)
    # TPDF: sum of two uniform distributions = triangular distribution
    dither = (
        rng.uniform(-0.5, 0.5, samples.shape) + rng.uniform(-0.5, 0.5, samples.shape)
    ) * quant_step
    return samples + dither


def _float_to_int16(samples: FloatArray, dither: bool = True) -> NDArray[np.int16]:
    """Clip, dither, and convert float64 [-1, 1] to int16."""
    clipped = np.clip(samples, -1.0, 1.0)
    if dither:
        clipped = _tpdf_dither(clipped, bit_depth=16)
        clipped = np.clip(clipped, -1.0, 1.0)
    return (clipped * 32767).astype(np.int16)


def _float_to_int24_bytes(samples: FloatArray, dither: bool = True) -> bytes:
    """Convert float64 [-1,1] to raw 24-bit PCM bytes (little-endian) with TPDF dithering."""
    clipped = np.clip(samples, -1.0, 1.0)
    if dither:
        clipped = _tpdf_dither(clipped, bit_depth=24)
        clipped = np.clip(clipped, -1.0, 1.0)
    ints = (clipped * 8388607).astype(np.int32)
    flat = ints.flatten()
    buf = bytearray(len(flat) * 3)
    for i in range(len(flat)):
        v = int(flat[i])
        b = v.to_bytes(3, byteorder="little", signed=True)
        buf[i * 3] = b[0]
        buf[i * 3 + 1] = b[1]
        buf[i * 3 + 2] = b[2]
    return bytes(buf)


def _float_to_float32_bytes(samples: FloatArray) -> bytes:
    """Convert float64 to IEEE 754 float32 bytes. No dithering needed."""
    f32 = np.clip(samples, -1.0, 1.0).astype(np.float32)
    return f32.tobytes()


def export_wav(
    samples: FloatArray,
    path: str | Path,
    sample_rate: int = 44100,
    bit_depth: int = 24,
) -> Path:
    """Write stereo float64 samples to a WAV file.

    Bit depth options:
        16: CD quality (96 dB dynamic range). TPDF dithered.
        24: Studio master (144 dB dynamic range). TPDF dithered. Default.
        32: IEEE 754 float (1528 dB theoretical). No dithering needed.
            This is the DAW interchange format - full precision preserved.

    Args:
        samples:     Shape (N, 2) float64 array in range [-1, 1].
        path:        Output file path (will create directories).
        sample_rate: Sample rate in Hz.
        bit_depth:   16, 24, or 32 (default 24).

    Returns:
        Resolved Path of the written file.
    """
    out = Path(path).with_suffix(".wav")
    out.parent.mkdir(parents=True, exist_ok=True)

    if bit_depth == 32:
        # 32-bit float WAV uses format tag 3 (IEEE_FLOAT) not 1 (PCM).
        # Python's wave module only supports PCM, so we write raw RIFF.
        raw = _float_to_float32_bytes(samples)
        n_channels = 2
        bytes_per_sample = 4
        byte_rate = sample_rate * n_channels * bytes_per_sample
        block_align = n_channels * bytes_per_sample
        data_size = len(raw)
        # RIFF/WAVE header for IEEE float
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            36 + data_size,  # file size - 8
            b"WAVE",
            b"fmt ",
            16,  # fmt chunk size
            3,  # format tag: IEEE float
            n_channels,
            sample_rate,
            byte_rate,
            block_align,
            32,  # bits per sample
            b"data",
            data_size,
        )
        with open(str(out), "wb") as f:
            f.write(header)
            f.write(raw)
    elif bit_depth == 24:
        raw_bytes = _float_to_int24_bytes(samples)
        with wave.open(str(out), "w") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(3)
            wf.setframerate(sample_rate)
            wf.writeframes(raw_bytes)
    else:
        int_samples = _float_to_int16(samples)
        with wave.open(str(out), "w") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(int_samples.tobytes())

    return out


def export_mp3(
    samples: FloatArray,
    path: str | Path,
    sample_rate: int = 44100,
    bitrate: str = "320k",
    metadata: dict[str, str] | None = None,
) -> Path:
    """Write stereo float64 samples to an MP3 file via pydub + ffmpeg.

    Requires pydub and ffmpeg on PATH. 320kbps is Spotify's maximum ingest
    quality - use it.

    Args:
        samples:     Shape (N, 2) float64 array in range [-1, 1].
        path:        Output file path.
        sample_rate: Sample rate in Hz.
        bitrate:     MP3 bitrate string (default '320k').
        metadata:    Optional dict of ID3 tags (artist, title, album, year).

    Returns:
        Resolved Path of the written file.
    """
    try:
        from pydub import AudioSegment
    except ImportError as e:
        raise ImportError("pydub is required for MP3 export: pip install pydub") from e

    out = Path(path).with_suffix(".mp3")
    out.parent.mkdir(parents=True, exist_ok=True)

    # Write to an in-memory WAV first, then transcode
    wav_buf = io.BytesIO()
    int_samples = _float_to_int16(samples)
    with wave.open(wav_buf, "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int_samples.tobytes())
    wav_buf.seek(0)

    segment = AudioSegment.from_wav(wav_buf)
    tags = metadata or {}
    segment.export(str(out), format="mp3", bitrate=bitrate, tags=tags)
    return out


def _wav_buf(samples: FloatArray, sample_rate: int, bit_depth: int = 16) -> io.BytesIO:
    """Build an in-memory WAV buffer from float64 stereo samples."""
    buf = io.BytesIO()
    if bit_depth == 24:
        raw = _float_to_int24_bytes(samples)
        with wave.open(buf, "w") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(3)
            wf.setframerate(sample_rate)
            wf.writeframes(raw)
    else:
        int_samples = _float_to_int16(samples)
        with wave.open(buf, "w") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(int_samples.tobytes())
    buf.seek(0)
    return buf


def export_ogg(
    samples: FloatArray,
    path: str | Path,
    sample_rate: int = 44100,
    quality: float = 8.0,
    metadata: dict[str, str] | None = None,
) -> Path:
    """Write stereo float64 samples to an OGG Vorbis file via pydub + ffmpeg.

    Args:
        quality:  Vorbis quality 0-10 (default 8, about 256kbps). Spotify accepts OGG.
        metadata: Optional dict of Vorbis comment tags (artist, title, album, year).
    """
    try:
        from pydub import AudioSegment
    except ImportError as e:
        raise ImportError("pydub is required for OGG export: pip install pydub") from e

    out = Path(path).with_suffix(".ogg")
    out.parent.mkdir(parents=True, exist_ok=True)
    segment = AudioSegment.from_wav(_wav_buf(samples, sample_rate))
    tags = metadata or {}
    segment.export(
        str(out),
        format="ogg",
        codec="libvorbis",
        parameters=["-q:a", str(quality)],
        tags=tags,
    )
    return out


def export_flac(
    samples: FloatArray,
    path: str | Path,
    sample_rate: int = 44100,
    bit_depth: int = 24,
    metadata: dict[str, str] | None = None,
) -> Path:
    """Write stereo float64 samples to a FLAC file (lossless) via pydub + ffmpeg.

    FLAC is lossless - bit-for-bit identical on decode. The bit_depth controls
    the precision of the source PCM before FLAC compression. 24-bit FLAC is
    the standard for streaming platform uploads (Spotify, Apple, Tidal).

    Args:
        bit_depth: 16 (CD) or 24 (hi-res). Default 24.
        metadata:  Optional dict of Vorbis comment tags (artist, title, album, year).
    """
    try:
        from pydub import AudioSegment
    except ImportError as e:
        raise ImportError("pydub is required for FLAC export: pip install pydub") from e

    out = Path(path).with_suffix(".flac")
    out.parent.mkdir(parents=True, exist_ok=True)
    # Use 24-bit WAV source for maximum FLAC quality
    bd = min(bit_depth, 24)  # FLAC maxes at 24-bit
    segment = AudioSegment.from_wav(_wav_buf(samples, sample_rate, bit_depth=bd))
    tags = metadata or {}
    segment.export(str(out), format="flac", tags=tags)
    return out
