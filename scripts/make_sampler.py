"""Album sampler: mix the first ~10-15 seconds of each track into a 2-min preview.

Creates a single audio file that previews all tracks in an album,
useful for sharing or embedding in the web player.

Usage:
    python scripts/make_sampler.py --album jazz_neosoul
    python scripts/make_sampler.py --all
    make sampler-anthology
"""

from __future__ import annotations

import argparse
import importlib
import wave
from pathlib import Path

import numpy as np

REPO = Path(__file__).parent.parent
FADE_SEC = 1.5  # crossfade between tracks
CLIP_SEC = 15.0  # seconds per track in sampler

RESET = "\033[0m"
GREEN = "\033[92m"
DIM = "\033[2m"


def _read_wav(path: Path, target_sr: int = 44100) -> np.ndarray | None:
    """Read a WAV file → float64 stereo array."""
    if not path.exists():
        return None
    with wave.open(str(path), "rb") as wf:
        sr = wf.getframerate()
        n_ch = wf.getnchannels()
        sampw = wf.getsampwidth()
        n = wf.getnframes()
        raw = wf.readframes(n)
    dtype = np.int16 if sampw == 2 else np.int32
    s = np.frombuffer(raw, dtype=dtype).astype(np.float64)
    s /= 32768.0 if sampw == 2 else 2147483648.0
    if n_ch == 1:
        s = np.column_stack([s, s])
    elif n_ch == 2:
        s = s.reshape(-1, 2)

    if sr != target_sr:
        from scipy import signal as scipy_sig

        new_len = int(len(s) * target_sr / sr)
        sl = scipy_sig.resample(s[:, 0], new_len)
        sr2 = scipy_sig.resample(s[:, 1], new_len)
        s = np.column_stack([sl, sr2])

    return s.astype(np.float64)


def _crossfade(a: np.ndarray, b: np.ndarray, fade_samples: int) -> np.ndarray:
    """Crossfade the end of `a` into the start of `b`."""
    fade_samples = min(fade_samples, len(a), len(b))
    fade_out = np.linspace(1, 0, fade_samples)
    fade_in = np.linspace(0, 1, fade_samples)

    result = a.copy()
    result[-fade_samples:] = (
        a[-fade_samples:] * fade_out[:, None] + b[:fade_samples] * fade_in[:, None]
    )
    return np.vstack([result, b[fade_samples:]])


def make_sampler(
    album_stem: str, out_path: Path | None = None, clip_sec: float = CLIP_SEC, sr: int = 44100
) -> Path | None:
    """Build a sampler mix for an album."""
    # Load album definition
    spec = importlib.util.spec_from_file_location("_alb", REPO / "albums" / f"{album_stem}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    album = mod.ALBUM
    tracks = album["tracks"]

    wav_dir = REPO / "dist" / "wav"
    clips: list[np.ndarray] = []
    clip_samples = int(clip_sec * sr)
    fade_samples = int(FADE_SEC * sr)

    print(f"  {album['title']}  ({len(tracks)} tracks)")
    for track in tracks:
        stem = track["song"]
        wav = wav_dir / f"{stem}.wav"
        s = _read_wav(wav, sr)
        if s is None:
            print(f"    skip {stem} (not rendered)")
            continue
        # Take from middle of track (more interesting than start)
        start = min(int(len(s) * 0.2), max(0, len(s) // 2 - clip_samples // 2))
        clip = s[start : start + clip_samples]
        if len(clip) < clip_samples:
            clip = np.vstack([clip, np.zeros((clip_samples - len(clip), 2))])
        clips.append(clip)
        print(f"    ✓ {track.get('title', stem)}")

    if not clips:
        print("  No clips rendered. Run: make songs-wav")
        return None

    # Crossfade all clips together
    mix = clips[0]
    for clip in clips[1:]:
        mix = _crossfade(mix, clip, fade_samples)

    # Fade in/out the whole sampler
    fi = int(sr * 2)  # 2s fade in
    fo = int(sr * 3)  # 3s fade out
    if fi < len(mix):
        mix[:fi] *= np.linspace(0, 1, fi)[:, None]
    if fo < len(mix):
        mix[-fo:] *= np.linspace(1, 0, fo)[:, None]

    # Normalize
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.92

    if out_path is None:
        out_path = REPO / "dist" / "samplers" / f"{album_stem}_sampler.wav"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Write WAV
    int_samples = np.clip(mix, -1.0, 1.0)
    int_samples = (int_samples * 32767).astype(np.int16)
    with wave.open(str(out_path), "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(int_samples.tobytes())

    dur = len(mix) / sr
    print(f"  {GREEN}→ {out_path.name}  ({dur:.0f}s){RESET}")
    return out_path


def main() -> None:
    from albums.render import discover_albums

    parser = argparse.ArgumentParser(description="Build album sampler previews")
    parser.add_argument("--album", help="Single album stem")
    parser.add_argument("--all", action="store_true")
    parser.add_argument(
        "--clip-sec", type=float, default=CLIP_SEC, help="Seconds per track (default 15)"
    )
    args = parser.parse_args()

    stems = discover_albums() if args.all else ([args.album] if args.album else [])
    if not stems:
        parser.print_help()
        return

    for stem in stems:
        print(f"\n{stem}")
        make_sampler(stem, clip_sec=args.clip_sec)
    print()


if __name__ == "__main__":
    main()
