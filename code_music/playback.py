"""Real-time audio playback for code-music songs.

Uses sounddevice for cross-platform streaming. Falls back to a temporary
WAV + system player (afplay/aplay/ffplay) when sounddevice is unavailable.

Usage::

    from code_music import Song, Track, Note
    from code_music.playback import play

    song = Song(title="Quick Test", bpm=120)
    tr = song.add_track(Track(instrument="piano"))
    tr.extend([Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)])

    play(song)  # renders then streams in real time
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from .engine import Song


def _has_sounddevice() -> bool:
    try:
        import sounddevice  # noqa: F401

        return True
    except (ImportError, OSError):
        return False


def _play_sounddevice(samples: np.ndarray, sample_rate: int, title: str) -> None:
    """Stream rendered audio via sounddevice (blocking)."""
    import sounddevice as sd

    duration = samples.shape[0] / sample_rate
    print(f"  Playing '{title}' — {duration:.1f}s ...")

    # sounddevice expects float32 in [-1, 1]
    audio = samples.astype(np.float32)
    sd.play(audio, samplerate=sample_rate)
    sd.wait()
    print("  Done.")


def _system_player() -> str | None:
    """Find a system audio player command."""
    for cmd in ("afplay", "aplay", "ffplay", "paplay"):
        if shutil.which(cmd):
            return cmd
    return None


def _play_fallback(samples: np.ndarray, sample_rate: int, title: str) -> None:
    """Write a temp WAV and play it with a system command."""
    from .export import export_wav

    player = _system_player()
    if player is None:
        print(
            "error: no audio player found. Install sounddevice (pip install sounddevice) "
            "or ensure afplay/aplay/ffplay is on PATH.",
            file=sys.stderr,
        )
        return

    duration = samples.shape[0] / sample_rate
    print(f"  Playing '{title}' — {duration:.1f}s (via {player}) ...")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        export_wav(samples, tmp_path, sample_rate)
        args = [player, str(tmp_path)]
        if player == "ffplay":
            args = [player, "-nodisp", "-autoexit", str(tmp_path)]
        subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        tmp_path.unlink(missing_ok=True)

    print("  Done.")


def play(song: "Song", bpm: float | None = None) -> None:
    """Render a Song and play it immediately.

    Tries sounddevice first for clean streaming; falls back to a system
    player (afplay on macOS, aplay on Linux) if sounddevice isn't installed.

    Args:
        song: A Song object to render and play.
        bpm:  Optional BPM override (applied before render).
    """
    from .synth import Synth

    if bpm is not None:
        song.bpm = bpm

    print(f"  Rendering '{song.title}' — {song.duration_sec:.1f}s @ {song.bpm} BPM ...")
    t0 = time.monotonic()
    samples = Synth(sample_rate=song.sample_rate).render_song(song)
    elapsed = time.monotonic() - t0
    print(f"  Rendered in {elapsed:.1f}s")

    if _has_sounddevice():
        _play_sounddevice(samples, song.sample_rate, song.title)
    else:
        _play_fallback(samples, song.sample_rate, song.title)
