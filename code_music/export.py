"""Export rendered audio to WAV or MP3.

Requires:
    WAV: scipy (stdlib-adjacent, always available)
    MP3: pydub + ffmpeg installed on PATH
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
    samples: FloatArray, path: str | Path, sample_rate: int = 44100, bitrate: str = "320k"
) -> Path:
    """Write stereo float64 samples to an MP3 file via pydub + ffmpeg.

    Requires pydub and ffmpeg on PATH. 320kbps is Spotify's maximum ingest
    quality — use it.

    Args:
        samples: Shape (N, 2) float64 array in range [-1, 1].
        path: Output file path.
        sample_rate: Sample rate in Hz.
        bitrate: MP3 bitrate string (default '320k').

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
    segment.export(str(out), format="mp3", bitrate=bitrate)
    return out
