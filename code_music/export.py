"""Export rendered audio to WAV, MP3, OGG, or FLAC.

Requires:
    WAV:  stdlib wave module (always available)
    MP3:  pydub + ffmpeg on PATH
    OGG:  pydub + ffmpeg on PATH
    FLAC: pydub + ffmpeg on PATH (lossless, preferred for mastering)
"""

from __future__ import annotations

import io
import wave
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def _float_to_int16(samples: FloatArray) -> NDArray[np.int16]:
    """Clip and convert float64 [-1, 1] to int16."""
    clipped = np.clip(samples, -1.0, 1.0)
    return (clipped * 32767).astype(np.int16)


def _float_to_int24_bytes(samples: FloatArray) -> bytes:
    """Convert float64 [-1,1] to raw 24-bit PCM bytes (little-endian)."""
    clipped = np.clip(samples, -1.0, 1.0)
    ints = (clipped * 8388607).astype(np.int32)
    # Pack each int32 as 3 bytes LE
    flat = ints.flatten()
    buf = bytearray()
    for v in flat:
        buf += v.to_bytes(3, byteorder="little", signed=True)
    return bytes(buf)


def export_wav(samples: FloatArray, path: str | Path, sample_rate: int = 44100) -> Path:
    """Write stereo float64 samples to a WAV file.

    Args:
        samples: Shape (N, 2) float64 array in range [-1, 1].
        path: Output file path (will create directories).
        sample_rate: Sample rate in Hz.

    Returns:
        Resolved Path of the written file.
    """
    out = Path(path).with_suffix(".wav")
    out.parent.mkdir(parents=True, exist_ok=True)

    int_samples = _float_to_int16(samples)

    with wave.open(str(out), "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)  # 16-bit = 2 bytes
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


def _wav_buf(samples: FloatArray, sample_rate: int) -> io.BytesIO:
    """Build an in-memory WAV buffer from float64 stereo samples."""
    buf = io.BytesIO()
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
    metadata: dict[str, str] | None = None,
) -> Path:
    """Write stereo float64 samples to a FLAC file (lossless) via pydub + ffmpeg.

    FLAC is lossless and the best option for archival / DAW round-tripping.
    Spotify accepts FLAC for upload via Spotify for Artists.

    Args:
        metadata: Optional dict of Vorbis comment tags (artist, title, album, year).
    """
    try:
        from pydub import AudioSegment
    except ImportError as e:
        raise ImportError("pydub is required for FLAC export: pip install pydub") from e

    out = Path(path).with_suffix(".flac")
    out.parent.mkdir(parents=True, exist_ok=True)
    segment = AudioSegment.from_wav(_wav_buf(samples, sample_rate))
    tags = metadata or {}
    segment.export(str(out), format="flac", tags=tags)
    return out
