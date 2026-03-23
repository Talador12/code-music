"""CLI entry point: python -m code_music or `code-music` after install."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


def _load_song(script: Path):
    """Import a song script and return its `song` variable."""
    spec = importlib.util.spec_from_file_location("song_module", script)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load {script}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    if not hasattr(mod, "song"):
        raise AttributeError(f"{script} must define a top-level `song` variable")
    return mod.song


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="code-music",
        description="Render a code-music script to WAV, MP3, OGG, or FLAC.",
    )
    parser.add_argument("script", type=Path, help="Python song script (must define `song`)")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output file path (default: <title>.<fmt> next to script)",
    )
    fmt_group = parser.add_mutually_exclusive_group()
    fmt_group.add_argument("--mp3", action="store_true", help="Export as MP3 (lossy, 320kbps)")
    fmt_group.add_argument("--ogg", action="store_true", help="Export as OGG Vorbis (lossy)")
    fmt_group.add_argument("--flac", action="store_true", help="Export as FLAC (lossless)")
    parser.add_argument("--bpm", type=float, default=None, help="Override song BPM")
    args = parser.parse_args(argv)

    script: Path = args.script.resolve()
    if not script.exists():
        print(f"error: {script} not found", file=sys.stderr)
        return 1

    print(f"Loading {script.name}...")
    song = _load_song(script)

    if args.bpm is not None:
        song.bpm = args.bpm
        print(f"BPM overridden to {song.bpm}")

    from .export import export_flac, export_mp3, export_ogg, export_wav
    from .synth import Synth

    print(f"Rendering '{song.title}' — {song.duration_sec:.1f}s at {song.bpm} BPM ...")
    synth = Synth(sample_rate=song.sample_rate)
    samples = synth.render_song(song)

    # Determine output suffix
    if args.mp3:
        suffix = ".mp3"
    elif args.ogg:
        suffix = ".ogg"
    elif args.flac:
        suffix = ".flac"
    else:
        suffix = ".wav"

    out_path = args.output
    if out_path is None:
        safe = song.title.lower().replace(" ", "_")
        out_path = script.parent / f"{safe}{suffix}"

    if args.mp3:
        result = export_mp3(samples, out_path, song.sample_rate)
    elif args.ogg:
        result = export_ogg(samples, out_path, song.sample_rate)
    elif args.flac:
        result = export_flac(samples, out_path, song.sample_rate)
    else:
        result = export_wav(samples, out_path, song.sample_rate)

    print(f"Exported: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
