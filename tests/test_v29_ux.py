"""Tests for v2.9 UX improvements: CLI fixes, repr, scaffold, list-instruments."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from code_music.engine import Note, Song, Track

ROOT = Path(__file__).resolve().parents[1]


class TestTrackRepr:
    def test_repr_is_concise(self):
        t = Track(name="lead", instrument="piano", volume=0.7)
        t.add(Note("C", 4, 1.0))
        t.add(Note("E", 4, 1.0))
        r = repr(t)
        assert "Track(" in r
        assert "lead" in r
        assert "piano" in r
        assert "beats=2" in r
        # Should NOT contain the actual beat objects
        assert "Beat(" not in r

    def test_repr_empty_track(self):
        t = Track(instrument="sine")
        r = repr(t)
        assert "beats=0" in r


class TestSongRepr:
    def test_repr_is_concise(self):
        song = Song(title="Test Song", bpm=140)
        tr = song.add_track(Track(name="pad", instrument="pad"))
        tr.add(Note("C", 4, 4.0))
        r = repr(song)
        assert "Song(" in r
        assert "Test Song" in r
        assert "bpm=140" in r
        assert "tracks=1" in r
        # Should NOT dump all dataclass fields
        assert "voice_tracks" not in r

    def test_repr_truncates_track_names(self):
        song = Song(title="Big", bpm=120)
        for i in range(8):
            tr = song.add_track(Track(name=f"t{i}", instrument="sine"))
            tr.add(Note("C", 4, 1.0))
        r = repr(song)
        assert "..." in r


class TestCLIImportMidiNoScript:
    def test_import_midi_works_without_script_arg(self):
        # Create a simple MIDI file first
        from code_music.midi import export_midi

        song = Song(title="MIDI Test", bpm=120)
        tr = song.add_track(Track(instrument="piano"))
        tr.add(Note("C", 4, 1.0))

        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            mid_path = Path(f.name)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_path = Path(f.name)
        try:
            export_midi(song, mid_path)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "code_music.cli",
                    "--import-midi",
                    str(mid_path),
                    "-o",
                    str(wav_path),
                ],
                capture_output=True,
                text=True,
                cwd=str(ROOT),
            )
            assert result.returncode == 0
        finally:
            mid_path.unlink(missing_ok=True)
            wav_path.unlink(missing_ok=True)


class TestCLIListInstruments:
    def test_list_instruments_shows_instruments(self):
        result = subprocess.run(
            [sys.executable, "-m", "code_music.cli", "--list-instruments"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        assert result.returncode == 0
        assert "piano" in result.stdout
        assert "bass" in result.stdout
        assert "sawtooth" in result.stdout
        assert "instruments available" in result.stdout


class TestCLINew:
    def test_new_creates_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "my_new_song.py"
            result = subprocess.run(
                [sys.executable, "-m", "code_music.cli", "--new", str(path)],
                capture_output=True,
                text=True,
                cwd=str(ROOT),
            )
            assert result.returncode == 0
            assert path.exists()
            content = path.read_text()
            assert "song = Song(" in content
            assert "My New Song" in content

    def test_new_refuses_overwrite(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            path = Path(f.name)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "code_music.cli", "--new", str(path)],
                capture_output=True,
                text=True,
                cwd=str(ROOT),
            )
            assert result.returncode != 0
            assert "already exists" in result.stderr
        finally:
            path.unlink(missing_ok=True)


class TestCLIHelpText:
    def test_help_includes_examples(self):
        result = subprocess.run(
            [sys.executable, "-m", "code_music.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        assert result.returncode == 0
        assert "examples:" in result.stdout
        assert "--play" in result.stdout
        assert "--flac" in result.stdout
        assert "--list-instruments" in result.stdout


class TestCLINoScriptError:
    def test_no_script_gives_clear_error(self):
        result = subprocess.run(
            [sys.executable, "-m", "code_music.cli"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        assert result.returncode != 0
