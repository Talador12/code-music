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

    if getattr(args, "genre_transform", None):
        from .transform import genre_transform as _gt

        song = _gt(song, args.genre_transform)
        print(f"  Transformed to {args.genre_transform}: '{song.title}'")

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
  code-music --random                   generate and play a random song
  code-music --random jazz              generate and play a jazz song
  code-music compose "jazz in Bb"       generate from natural language prompt
  code-music analyze my_song.py         print full analysis report
  code-music --repl                     interactive music coding REPL
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
        help="Python song script (must define `song`), or subcommand: compose, analyze",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress output (only show errors and final path)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed progress (track-level timing, effect chain info)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate song script without rendering (check imports, song object, tracks)",
    )
    parser.add_argument(
        "--genre-transform",
        type=str,
        default=None,
        metavar="GENRE",
        help="Transform the song into a different genre before rendering "
        "(e.g. --genre-transform jazz). Use --list-genres to see all options.",
    )
    parser.add_argument(
        "--list-genres",
        action="store_true",
        help="List all available genres for --genre-transform and exit",
    )
    parser.add_argument(
        "--quality",
        type=str,
        default=None,
        metavar="PRESET",
        help="Export with a named quality preset (e.g. --quality spotify-upload, "
        "--quality apple-lossless, --quality archive-master). "
        "Use --list-quality to see all options.",
    )
    parser.add_argument(
        "--list-quality",
        action="store_true",
        help="List all quality presets (platform-specific export settings) and exit",
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
        "--random",
        nargs="?",
        const="",
        default=None,
        metavar="GENRE",
        help="Generate and play a random song (lo_fi, jazz, ambient, edm, rock, ...)",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show song metadata (title, BPM, duration, tracks) without rendering",
    )
    parser.add_argument(
        "--repl",
        action="store_true",
        help="Start interactive music coding REPL with all imports pre-loaded",
    )
    parser.add_argument(
        "--compose",
        nargs="+",
        default=None,
        metavar="WORD",
        help="Natural language song prompt, e.g. --compose jazz ballad in Bb at 90 bpm",
    )
    parser.add_argument(
        "--list-scales",
        action="store_true",
        help="Show all available scales with interval patterns",
    )
    parser.add_argument(
        "--list-chords",
        action="store_true",
        help="Show all available chord shapes with intervals",
    )
    parser.add_argument(
        "--track-waveforms",
        type=str,
        default=None,
        nargs="?",
        const="auto",
        metavar="PATH",
        help="Export per-track waveform SVG",
    )
    parser.add_argument(
        "--sheet-music",
        type=str,
        default=None,
        nargs="?",
        const="auto",
        metavar="PATH",
        help="Export sheet music SVG for first track (or use --track N)",
    )
    parser.add_argument(
        "--track",
        type=int,
        default=0,
        help="Track index for --sheet-music (default: 0)",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Print a full analysis report for the song (no audio render)",
    )
    parser.add_argument(
        "--master",
        type=Path,
        default=None,
        metavar="FILE",
        help="Master a WAV file: normalize LUFS, true peak limit, dither. "
        "Output to <name>_mastered.<fmt>",
    )
    parser.add_argument(
        "--target-lufs",
        type=float,
        default=-14.0,
        help="Target LUFS for mastering (default: -14.0, Spotify standard)",
    )
    parser.add_argument(
        "--stems",
        action="store_true",
        help="Export individual track stems instead of mixed audio",
    )
    parser.add_argument(
        "--merge",
        type=Path,
        default=None,
        metavar="FILE",
        help="Merge another song script into this one (overlay tracks at beat 0)",
    )
    parser.add_argument(
        "--piano-roll",
        type=str,
        default=None,
        nargs="?",
        const="auto",
        metavar="PATH",
        help="Export piano roll SVG (default: <song>_piano_roll.svg)",
    )
    parser.add_argument(
        "--spectrogram",
        type=str,
        default=None,
        nargs="?",
        const="auto",
        metavar="PATH",
        help="Export spectrogram SVG (default: <song>_spectrogram.svg)",
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

    # Helper for quiet mode
    def _print(msg: str) -> None:
        if not args.quiet:
            print(msg)

    # ── Standalone commands (no script required) ─────────────────────────
    if args.list_genres:
        from .transform import list_genres

        genres = list_genres()
        print(f"{len(genres)} genres available for --genre-transform:\n")
        for g in genres:
            print(f"  {g}")
        return 0

    if args.list_quality:
        from .export import list_quality_presets

        presets = list_quality_presets()
        print(f"{len(presets)} quality presets available:\n")
        for p in presets:
            print(
                f"  {p['name']:20s} {p['format']:4s} {p['bit_depth']:2s}-bit "
                f"{p['sample_rate']:>5s}Hz  {p['description']}"
            )
        return 0

    if args.list_instruments:
        from .synth import Synth

        instruments = sorted(Synth.PRESETS.keys())
        print(f"{len(instruments)} instruments available:\n")
        for name in instruments:
            print(f"  {name}")
        return 0

    if args.list_scales:
        from .engine import SCALES

        print(f"{len(SCALES)} scales available:\n")
        for name in sorted(SCALES.keys()):
            intervals = SCALES[name]
            pattern = "-".join(str(i) for i in intervals)
            print(f"  {name:25s} [{pattern}]")
        return 0

    if args.list_chords:
        from .engine import CHORD_SHAPES

        print(f"{len(CHORD_SHAPES)} chord shapes available:\n")
        for name in sorted(CHORD_SHAPES.keys()):
            intervals = CHORD_SHAPES[name]
            print(f"  {name:15s} {intervals}")
        return 0

    if args.new:
        return _scaffold_song(args.new)

    if args.repl:
        from .repl import start_repl

        start_repl(bpm=args.bpm or 120)
        return 0

    if args.master:
        import numpy as np

        from .mastering import master_audio, measure_lufs

        wav_path = args.master.resolve()
        if not wav_path.exists():
            print(f"error: {wav_path} not found", file=sys.stderr)
            return 1

        # Read WAV
        try:
            from scipy.io import wavfile

            sr, raw = wavfile.read(str(wav_path))
        except Exception as e:
            print(f"error reading {wav_path.name}: {e}", file=sys.stderr)
            return 1

        # Convert to float64 stereo
        audio = raw.astype(np.float64)
        if audio.ndim == 1:
            audio = np.column_stack([audio, audio])
        if audio.max() > 1.0:
            audio = audio / 32768.0  # int16 to float

        input_lufs = measure_lufs(audio, sr)
        target = args.target_lufs
        print(f"  Mastering '{wav_path.name}'")
        print(f"  Input: {input_lufs:.1f} LUFS, {sr} Hz, {audio.shape[0] / sr:.1f}s")
        print(f"  Target: {target:.1f} LUFS")

        t0 = time.monotonic()
        mastered = master_audio(audio, sr, target_lufs=target)
        elapsed = time.monotonic() - t0

        output_lufs = measure_lufs(mastered, sr)
        print(f"  Output: {output_lufs:.1f} LUFS (processed in {elapsed:.2f}s)")

        # Determine output format and path
        if args.flac:
            suffix = ".flac"
        elif args.mp3:
            suffix = ".mp3"
        elif args.ogg:
            suffix = ".ogg"
        else:
            suffix = ".wav"

        if args.output:
            out_path = args.output
        else:
            out_path = wav_path.with_stem(wav_path.stem + "_mastered").with_suffix(suffix)

        from .export import export_flac, export_mp3, export_ogg, export_wav

        if suffix == ".flac":
            result = export_flac(mastered, out_path, sr)
        elif suffix == ".mp3":
            result = export_mp3(mastered, out_path, sr)
        elif suffix == ".ogg":
            result = export_ogg(mastered, out_path, sr)
        else:
            result = export_wav(mastered, out_path, sr)

        print(f"  Exported: {result}")
        return 0

    # ── Positional subcommands: "compose" and "analyze" ─────────────────
    # Support: code-music compose "jazz in Bb" (in addition to --compose)
    if args.script is not None and args.script.name == "compose" and args.compose is None:
        # Treat remaining argv as the compose prompt
        remaining = argv[argv.index("compose") + 1 :] if argv else sys.argv[2:]
        if remaining:
            args.compose = remaining
            args.script = None
        else:
            print(
                'error: compose requires a prompt, e.g. code-music compose "jazz in Bb"',
                file=sys.stderr,
            )
            return 1

    if args.script is not None and args.script.name == "analyze" and not args.analyze:
        # Treat next arg as the script to analyze
        remaining = argv[argv.index("analyze") + 1 :] if argv else sys.argv[2:]
        if remaining:
            args.script = Path(remaining[0])
            args.analyze = True
        else:
            print("error: analyze requires a song script", file=sys.stderr)
            return 1

    if args.random is not None:
        import random as _rng

        from .engine import generate_song
        from .playback import play as _play

        genres = ["lo_fi", "jazz", "ambient", "edm", "rock", "classical", "funk", "hip_hop"]
        genre = args.random if args.random else _rng.choice(genres)
        if genre not in genres:
            print(f"error: unknown genre {genre!r}. Choose: {', '.join(genres)}", file=sys.stderr)
            return 1
        seed = _rng.randint(0, 2**31)
        print(f"  Generating {genre} song (seed={seed})...")
        song = generate_song(genre, bars=16, seed=seed, sample_rate=22050)
        if args.bpm:
            song.bpm = args.bpm
        _play(song)
        return 0

    # ── Compose mode (natural language → Song) ──────────────────────────
    if args.compose is not None:
        from .theory import compose as _compose

        prompt = " ".join(args.compose)
        if not prompt.strip():
            print("error: compose requires a prompt, e.g. --compose jazz in Bb", file=sys.stderr)
            return 1

        import random as _rng2

        seed = _rng2.randint(0, 2**31)
        print(f'  Composing: "{prompt}" (seed={seed})...')
        song = _compose(prompt, seed=seed)
        if args.bpm:
            song.bpm = args.bpm
        print(f'  Generated: "{song.title}" — {song.bpm:.0f} BPM, {len(song.tracks)} tracks')

        if args.play:
            from .playback import play as _play2

            _play2(song)
        elif args.output or args.flac or args.mp3 or args.ogg or args.midi:
            from .export import export_flac, export_mp3, export_ogg, export_wav
            from .synth import Synth

            t0 = time.monotonic()
            samples = Synth(song.sample_rate).render_song(song)
            elapsed = time.monotonic() - t0
            print(f"  Rendered in {elapsed:.1f}s")

            if args.midi:
                from .midi import export_midi

                suffix = ".mid"
            elif args.mp3:
                suffix = ".mp3"
            elif args.ogg:
                suffix = ".ogg"
            elif args.flac:
                suffix = ".flac"
            else:
                suffix = ".wav"

            out_path = args.output or Path(song.title.lower().replace(" ", "_") + suffix)
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
        else:
            from .playback import play as _play3

            _play3(song)
        return 0

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

    # ── Dry run: validate without rendering ─────────────────────────────
    if args.dry_run:
        try:
            song = _load_song(script)
        except Exception as e:
            print(f"FAIL: {script.name}: {e}", file=sys.stderr)
            return 1
        if args.bpm:
            song.bpm = args.bpm
        info = song.info()
        print(
            f"OK: '{info.get('title', '?')}' - {info.get('tracks', 0)} tracks, "
            f"{info.get('bpm', '?')} BPM, {info.get('duration', '?')}s"
        )
        return 0

    # ── Genre transform: convert before rendering ────────────────────────
    if args.genre_transform and args.script:
        from .transform import genre_transform as _genre_transform, GENRE_PROFILES

        if args.genre_transform not in GENRE_PROFILES:
            from .transform import list_genres

            print(
                f"error: unknown genre {args.genre_transform!r}. "
                f"Available: {', '.join(list_genres()[:10])}... (use --list-genres for all)",
                file=sys.stderr,
            )
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
    elif args.piano_roll is not None:
        try:
            song = _load_song(script)
        except Exception as e:
            print(f"error loading {script.name}: {e}", file=sys.stderr)
            return 1
        if args.bpm:
            song.bpm = args.bpm
        from .composition import to_piano_roll

        out_path = args.piano_roll if args.piano_roll != "auto" else f"{script.stem}_piano_roll.svg"
        svg = to_piano_roll(song, path=out_path)
        print(f"  Piano roll: {out_path} ({len(svg)} chars)")
        return 0
    elif args.spectrogram is not None:
        try:
            song = _load_song(script)
        except Exception as e:
            print(f"error loading {script.name}: {e}", file=sys.stderr)
            return 1
        if args.bpm:
            song.bpm = args.bpm
        from .composition import to_spectrogram

        out_path = (
            args.spectrogram if args.spectrogram != "auto" else f"{script.stem}_spectrogram.svg"
        )
        svg = to_spectrogram(song, path=out_path)
        print(f"  Spectrogram: {out_path} ({len(svg)} chars)")
        return 0
    elif args.track_waveforms is not None:
        try:
            song = _load_song(script)
        except Exception as e:
            print(f"error loading {script.name}: {e}", file=sys.stderr)
            return 1
        if args.bpm:
            song.bpm = args.bpm
        from .composition import to_track_waveforms

        out_path = (
            args.track_waveforms
            if args.track_waveforms != "auto"
            else f"{script.stem}_track_waveforms.svg"
        )
        svg = to_track_waveforms(song, path=out_path)
        print(f"  Track waveforms: {out_path} ({len(svg)} chars)")
        return 0
    elif args.sheet_music is not None:
        try:
            song = _load_song(script)
        except Exception as e:
            print(f"error loading {script.name}: {e}", file=sys.stderr)
            return 1
        if args.bpm:
            song.bpm = args.bpm
        from .composition import to_sheet_music

        out_path = (
            args.sheet_music if args.sheet_music != "auto" else f"{script.stem}_sheet_music.svg"
        )
        svg = to_sheet_music(song, track_index=args.track, path=out_path)
        print(f"  Sheet music: {out_path} ({len(svg)} chars)")
        return 0
    elif args.analyze:
        try:
            song = _load_song(script)
        except Exception as e:
            print(f"error loading {script.name}: {e}", file=sys.stderr)
            return 1
        if args.bpm:
            song.bpm = args.bpm
        from .composition import full_analysis

        report = full_analysis(song)
        print(report)
        return 0
    elif args.merge:
        merge_script = args.merge.resolve()
        if not merge_script.exists():
            print(f"error: {merge_script} not found", file=sys.stderr)
            return 1
        try:
            song = _load_song(script)
            other = _load_song(merge_script)
        except Exception as e:
            print(f"error loading songs: {e}", file=sys.stderr)
            return 1
        if args.bpm:
            song.bpm = args.bpm

        from .automation import song_overlay

        song_overlay(song, other, at_beat=0.0)
        print(f"  Merged '{other.title}' into '{song.title}' ({len(song.tracks)} tracks total)")

        # Render the merged result
        from .export import export_wav
        from .synth import Synth

        t0 = time.monotonic()
        samples = Synth(song.sample_rate).render_song(song)
        elapsed = time.monotonic() - t0
        print(f"  Rendered in {elapsed:.1f}s")
        out_path = args.output or Path(f"{script.stem}_merged.wav")
        result = export_wav(samples, out_path, song.sample_rate)
        print(f"  Exported: {result}")
        return 0
    elif args.stems:
        try:
            song = _load_song(script)
        except Exception as e:
            print(f"error loading {script.name}: {e}", file=sys.stderr)
            return 1
        if args.bpm:
            song.bpm = args.bpm

        out_dir = args.output or (script.parent / f"{script.stem}_stems")
        fmt = "flac" if args.flac else ("mp3" if args.mp3 else "wav")
        print(f"  Exporting stems for '{song.title}' ({len(song.tracks)} tracks) ...")
        t0 = time.monotonic()
        paths = song.export_stems(str(out_dir), fmt=fmt)
        elapsed = time.monotonic() - t0
        print(f"  Exported {len(paths)} stems in {elapsed:.1f}s → {out_dir}/")
        for p in paths:
            print(f"    {p.name}")
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
