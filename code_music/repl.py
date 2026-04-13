"""Interactive REPL for live music coding.

Usage::

    code-music --repl
    python -m code_music --repl

Drops into an interactive Python session with all code_music imports
pre-loaded. Special REPL commands:

    /play           Render and play the current `song`
    /add <code>     Execute code and play result
    /reset          Clear the song and start fresh
    /info           Print song metadata
    /tracks         List all tracks
    /export <path>  Export current song to file
    /bpm <n>        Change song BPM
    /help           Show REPL commands
    /quit           Exit
"""

from __future__ import annotations

import code
import sys
import traceback


_HELP_TEXT = """\
code-music REPL commands:
  /play             Render and play the current song
  /add <code>       Execute Python code and auto-play
  /reset            Clear all tracks, start fresh
  /info             Show song metadata (title, BPM, tracks, duration)
  /tracks           List all tracks with instrument and note count
  /export <path>    Export song to file (WAV/FLAC/MP3 by extension)
  /bpm <n>          Change song BPM
  /undo             Remove the last track added
  /help             Show this help
  /quit             Exit the REPL

All code_music names are pre-imported. The variable `song` is your
active Song object. Modify it directly:

  >>> tr = song.add_track(Track(name="bass", instrument="bass"))
  >>> tr.extend([Note("C", 2, 2.0), Note("G", 2, 2.0)])
  >>> /play
"""


def _play_song(song):
    """Render and play the current song."""
    try:
        from .playback import play

        play(song)
    except Exception as e:
        print(f"  error playing: {e}")


def _export_song(song, path_str: str):
    """Export current song to a file."""
    from pathlib import Path

    path = Path(path_str.strip())
    suffix = path.suffix.lower()

    try:
        from .synth import Synth

        samples = Synth(sample_rate=song.sample_rate).render_song(song)

        if suffix == ".flac":
            from .export import export_flac

            result = export_flac(samples, path, song.sample_rate)
        elif suffix == ".mp3":
            from .export import export_mp3

            result = export_mp3(samples, path, song.sample_rate)
        elif suffix == ".ogg":
            from .export import export_ogg

            result = export_ogg(samples, path, song.sample_rate)
        elif suffix == ".mid":
            from .midi import export_midi

            result = export_midi(song, path)
        else:
            from .export import export_wav

            result = export_wav(samples, path, song.sample_rate)

        print(f"  Exported: {result}")
    except Exception as e:
        print(f"  error exporting: {e}")


def _show_info(song):
    """Print song metadata."""
    info = song.info()
    for k, v in info.items():
        print(f"  {k}: {v}")


def _show_tracks(song):
    """List all tracks."""
    if not song.tracks:
        print("  (no tracks)")
        return
    for i, tr in enumerate(song.tracks):
        beat_count = len(tr.beats)
        print(f"  [{i}] {tr.name} ({tr.instrument}) - {beat_count} beats, vol={tr.volume:.2f}")


def _handle_slash_command(cmd: str, namespace: dict) -> bool:
    """Handle a /command. Returns True if handled, False if not a command."""
    if not cmd.startswith("/"):
        return False

    parts = cmd.split(None, 1)
    command = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""
    song = namespace.get("song")

    if command in ("/quit", "/exit", "/q"):
        print("Goodbye.")
        raise SystemExit(0)

    if command in ("/help", "/h", "/?"):
        print(_HELP_TEXT)
        return True

    if command == "/play":
        if song is not None:
            _play_song(song)
        else:
            print("  No song defined. Create one: song = Song(title='My Song', bpm=120)")
        return True

    if command == "/info":
        if song is not None:
            _show_info(song)
        else:
            print("  No song defined.")
        return True

    if command == "/tracks":
        if song is not None:
            _show_tracks(song)
        else:
            print("  No song defined.")
        return True

    if command == "/reset":
        from .engine import Song

        namespace["song"] = Song(title="REPL Session", bpm=120)
        print("  Song reset. Fresh start.")
        return True

    if command == "/bpm":
        if not arg:
            if song is not None:
                print(f"  BPM: {song.bpm}")
            return True
        try:
            bpm = float(arg)
            if song is not None:
                song.bpm = bpm
                print(f"  BPM set to {bpm}")
        except ValueError:
            print(f"  Invalid BPM: {arg}")
        return True

    if command == "/export":
        if not arg:
            print("  Usage: /export path.wav")
            return True
        if song is not None:
            _export_song(song, arg)
        else:
            print("  No song defined.")
        return True

    if command == "/undo":
        if song is not None and song.tracks:
            removed = song.tracks.pop()
            print(f"  Removed track: {removed.name}")
        else:
            print("  Nothing to undo.")
        return True

    if command == "/add":
        if not arg:
            print("  Usage: /add <python code>")
            return True
        try:
            exec(arg, namespace)
            if song:
                _play_song(song)
        except Exception:
            traceback.print_exc()
        return True

    print(f"  Unknown command: {command}. Type /help for options.")
    return True


class MusicConsole(code.InteractiveConsole):
    """Interactive console with music-specific slash commands."""

    def __init__(self, namespace: dict):
        super().__init__(locals=namespace)
        self._namespace = namespace

    def runsource(self, source, filename="<input>", symbol="single"):
        """Override to intercept slash commands."""
        stripped = source.strip()
        if stripped.startswith("/"):
            _handle_slash_command(stripped, self._namespace)
            return False  # not incomplete
        return super().runsource(source, filename, symbol)


def start_repl(bpm: float = 120):
    """Start the interactive music REPL.

    Pre-imports all code_music names into the namespace and creates
    a default Song object. Supports /play, /info, /export, etc.

    Args:
        bpm: Initial BPM for the default song.
    """
    # Build namespace with all code_music imports
    import code_music

    namespace: dict = {}

    # Import everything from code_music
    all_names = getattr(code_music, "__all__", [])
    for name in all_names:
        obj = getattr(code_music, name, None)
        if obj is not None:
            namespace[name] = obj

    # Also import key classes directly
    from .engine import Chord, Note, Song, Track

    namespace.update(
        {
            "Song": Song,
            "Track": Track,
            "Note": Note,
            "Chord": Chord,
        }
    )

    # Create default song
    song = Song(title="REPL Session", bpm=bpm)
    namespace["song"] = song

    # Import scale and other common helpers
    from .engine import scale

    namespace["scale"] = scale

    version = getattr(code_music, "__version__", "dev")

    banner = f"""\
code-music v{version} REPL
{len(all_names)} functions loaded. Type /help for commands.

  song = Song("REPL Session", bpm={bpm})

  Try:
    tr = song.add_track(Track(instrument="piano"))
    tr.extend(scale("C", "pentatonic", octave=4, length=8))
    /play
"""

    console = MusicConsole(namespace)
    console.interact(banner=banner, exitmsg="")
