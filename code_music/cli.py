"""CLI entry point: python -m code_music or `code-music` after install."""

from __future__ import annotations

import argparse
import importlib.util
import sys
import time
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


_STARTER_TEMPLATE = '''\
"""%(name)s — My new song.

Run:  code-music %(filename)s --play
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale

song = Song(title="%(title)s", bpm=120)

# Add tracks — try: piano, sawtooth, bass, pad, organ, pluck, drums_kick, drums_snare
melody = song.add_track(Track(name="melody", instrument="piano", volume=0.6))
melody.extend([
    Note("C", 4, 1.0),
    Note("E", 4, 1.0),
    Note("G", 4, 1.0),
    Note("C", 5, 2.0),
])

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
bass.extend([Note("C", 2, 2.0), Note("G", 2, 2.0)])

# Effects — reverb, delay, compress, distortion, lowpass, highpass, stereo_width, ...
song.effects = {
    "melody": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
}
'''


def _scaffold_song(path: Path) -> int:
    """Create a new starter song file at *path*."""
    if path.exists():
        print(f"error: {path} already exists", file=sys.stderr)
        return 1
    name = path.stem
    title = name.replace("_", " ").title()
    content = _STARTER_TEMPLATE % {"name": name, "filename": path.name, "title": title}
    path.write_text(content)
    print(f"  Created {path}")
    print(f"  Run: code-music {path} --play")
    return 0


def _play_once(script: Path, args) -> int:
    """Load a song and play it immediately without file export."""
    from .playback import play

    try:
        song = _load_song(script)
    except Exception as e:
        print(f"error loading {script.name}: {e}", file=sys.stderr)
        return 1

    play(song, bpm=args.bpm)
    return 0


def _render_once(script: Path, args) -> int:
    """Load, render, and export a single song. Returns exit code."""
    from .export import export_flac, export_mp3, export_ogg, export_wav
    from .midi import export_midi
    from .synth import Synth

    try:
        song = _load_song(script)
    except Exception as e:
        print(f"error loading {script.name}: {e}", file=sys.stderr)
        return 1

    if args.bpm is not None:
        song.bpm = args.bpm

    print(f"  Rendering '{song.title}' — {song.duration_sec:.1f}s @ {song.bpm} BPM ...")
    t0 = time.monotonic()
    synth = Synth(sample_rate=song.sample_rate)
    samples = synth.render_song(song)
    elapsed = time.monotonic() - t0
    print(f"  Rendered in {elapsed:.1f}s")

    # Determine format + path
    if args.midi:
        suffix = ".mid"
    elif args.mp3:
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

    if args.midi:
        result = export_midi(song, out_path)
    elif args.mp3:
        result = export_mp3(samples, out_path, song.sample_rate)
    elif args.ogg:
        result = export_ogg(samples, out_path, song.sample_rate)
    elif args.flac:
        result = export_flac(samples, out_path, song.sample_rate)
    else:
        result = export_wav(samples, out_path, song.sample_rate)

    print(f"  Exported: {result}")
    return 0


def main(argv: list[str] | None = None) -> int:
    from . import __version__

    epilog = """\
examples:
  code-music my_song.py                 render to WAV
  code-music my_song.py --play          render + play immediately
  code-music my_song.py --flac          render to FLAC (Spotify-ready)
  code-music my_song.py --watch --play  live coding: auto-play on save
  code-music my_song.py --info          show metadata without rendering
  code-music --import-midi song.mid     import MIDI → render to WAV
  code-music --new my_song.py           scaffold a starter song file
  code-music --list-instruments         show all available instruments
"""
    parser = argparse.ArgumentParser(
        prog="code-music",
        description="Write music in Python. Render to WAV, FLAC, MP3, MIDI — or play instantly.",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"code-music {__version__}")
    parser.add_argument(
        "script",
        type=Path,
        nargs="?",
        default=None,
        help="Python song script (must define `song`)",
    )
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
    fmt_group.add_argument("--midi", action="store_true", help="Export as MIDI (.mid)")
    parser.add_argument(
        "--play",
        action="store_true",
        help="Play immediately (combinable with --watch for live coding)",
    )
    parser.add_argument(
        "--import-midi",
        type=Path,
        default=None,
        metavar="FILE",
        help="Import a .mid file as a Song and render it",
    )
    parser.add_argument(
        "--new",
        type=Path,
        default=None,
        metavar="FILE",
        help="Scaffold a new starter song file",
    )
    parser.add_argument(
        "--list-instruments",
        action="store_true",
        help="List all available synth instruments and exit",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show song metadata (title, BPM, duration, tracks) without rendering",
    )
    parser.add_argument("--bpm", type=float, default=None, help="Override song BPM")
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Render and report timing without saving a file",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Re-render on file save (live coding mode). Polls every second.",
    )
    args = parser.parse_args(argv)

    # ── Standalone commands (no script required) ─────────────────────────
    if args.list_instruments:
        from .synth import Synth

        instruments = sorted(Synth.PRESETS.keys())
        print(f"{len(instruments)} instruments available:\n")
        for name in instruments:
            print(f"  {name}")
        return 0

    if args.new:
        return _scaffold_song(args.new)

    # ── MIDI import mode (no script required) ──────────────────────────
    if args.import_midi:
        from .midi import import_midi

        midi_path = args.import_midi.resolve()
        if not midi_path.exists():
            print(f"error: {midi_path} not found", file=sys.stderr)
            return 1

        print(f"Importing {midi_path.name}...")
        song = import_midi(midi_path)
        if args.bpm:
            song.bpm = args.bpm
        print(f"  Imported '{song.title}' — {len(song.tracks)} tracks, {song.bpm} BPM")

        out_path = args.output or midi_path.with_suffix(".wav")
        from .export import export_wav
        from .synth import Synth

        print(f"  Rendering '{song.title}' — {song.duration_sec:.1f}s ...")
        t0 = time.monotonic()
        samples = Synth(song.sample_rate).render_song(song)
        elapsed = time.monotonic() - t0
        print(f"  Rendered in {elapsed:.1f}s")
        result = export_wav(samples, out_path, song.sample_rate)
        print(f"  Exported: {result}")
        return 0

    # ── Normal script mode (script required from here) ─────────────────
    if args.script is None:
        parser.error(
            "a script argument is required (or use --import-midi, --new, --list-instruments)"
        )
    script: Path = args.script.resolve()
    if not script.exists():
        print(f"error: {script} not found", file=sys.stderr)
        return 1

    if args.benchmark:
        from .synth import Synth

        try:
            song = _load_song(script)
        except Exception as e:
            print(f"error loading {script.name}: {e}", file=sys.stderr)
            return 1
        if args.bpm:
            song.bpm = args.bpm
        print(f"  Benchmarking '{song.title}' — {song.duration_sec:.1f}s @ {song.bpm} BPM ...")
        t0 = time.monotonic()
        samples = Synth(song.sample_rate).render_song(song)
        elapsed = time.monotonic() - t0
        ratio = song.duration_sec / elapsed if elapsed > 0 else float("inf")
        print(f"  Rendered in {elapsed:.2f}s ({ratio:.1f}x realtime)")
        print(f"  {samples.shape[0]} samples, {samples.shape[1]} channels")
        return 0
    elif args.info:
        try:
            song = _load_song(script)
        except Exception as e:
            print(f"error loading {script.name}: {e}", file=sys.stderr)
            return 1
        if args.bpm:
            song.bpm = args.bpm
        info = song.info()
        for k, v in info.items():
            print(f"  {k}: {v}")
        return 0
    elif args.play and not args.watch:
        print(f"Loading {script.name}...")
        return _play_once(script, args)
    elif args.watch:
        mode = "render + play" if args.play else "render"
        print(f"Watching {script.name} ({mode}) — Ctrl+C to stop.")
        last_mtime = 0.0
        try:
            while True:
                mtime = script.stat().st_mtime
                if mtime != last_mtime:
                    last_mtime = mtime
                    print(f"\n[{time.strftime('%H:%M:%S')}] Change detected ...")
                    if args.play:
                        _play_once(script, args)
                    else:
                        _render_once(script, args)
                time.sleep(1.0)
        except KeyboardInterrupt:
            print("\nWatch mode stopped.")
            return 0
    else:
        print(f"Loading {script.name}...")
        return _render_once(script, args)


if __name__ == "__main__":
    sys.exit(main())
