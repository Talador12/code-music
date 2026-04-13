"""Tests for v140.0: mastering CLI, stem import, metadata embedding, --stems flag."""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Mastering CLI
# ---------------------------------------------------------------------------


class TestMasteringCLI(unittest.TestCase):
    """CLI --master flag masters WAV files."""

    def test_master_flag_in_help(self):
        from code_music.cli import main

        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                main(["--help"])
            except SystemExit:
                pass
        combined = out.getvalue() + err.getvalue()
        assert "master" in combined.lower()

    def test_target_lufs_flag_in_help(self):
        from code_music.cli import main

        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                main(["--help"])
            except SystemExit:
                pass
        combined = out.getvalue() + err.getvalue()
        assert "lufs" in combined.lower()

    def test_master_nonexistent_file(self):
        from code_music.cli import main

        result = main(["--master", "/nonexistent/file.wav"])
        assert result == 1

    def test_master_wav_file(self):
        """Master a real WAV file and verify output exists."""
        import wave

        from code_music.cli import main

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test WAV
            wav_path = Path(tmpdir) / "test.wav"
            sr = 22050
            duration = 0.5
            n_samples = int(sr * duration)
            audio = (np.sin(np.linspace(0, 440 * 2 * np.pi * duration, n_samples)) * 16000).astype(
                np.int16
            )
            stereo = np.column_stack([audio, audio])
            with wave.open(str(wav_path), "w") as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                wf.writeframes(stereo.tobytes())

            out = io.StringIO()
            with redirect_stdout(out):
                result = main(["--master", str(wav_path)])

            assert result == 0
            mastered_path = wav_path.with_stem("test_mastered")
            assert mastered_path.exists()
            mastered_path.unlink()  # cleanup


# ---------------------------------------------------------------------------
# Stems CLI
# ---------------------------------------------------------------------------


class TestStemsCLI(unittest.TestCase):
    """CLI --stems flag exports individual tracks."""

    def test_stems_flag_in_help(self):
        from code_music.cli import main

        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                main(["--help"])
            except SystemExit:
                pass
        combined = out.getvalue() + err.getvalue()
        assert "stems" in combined.lower()


# ---------------------------------------------------------------------------
# Song.import_stems
# ---------------------------------------------------------------------------


class TestImportStems(unittest.TestCase):
    """Import WAV files as SampleTracks."""

    def test_import_empty_dir(self):
        from code_music import Song

        with tempfile.TemporaryDirectory() as tmpdir:
            song = Song.import_stems(tmpdir, bpm=120)
            assert isinstance(song, Song)
            assert len(song.sample_tracks) == 0

    def test_import_with_wav_files(self):
        import wave

        from code_music import Song

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two test WAVs
            for name in ["kick", "snare"]:
                wav_path = Path(tmpdir) / f"{name}.wav"
                sr = 22050
                audio = np.zeros(sr, dtype=np.int16)  # 1s silence
                with wave.open(str(wav_path), "w") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sr)
                    wf.writeframes(audio.tobytes())

            song = Song.import_stems(tmpdir, bpm=120, title="Imported")
            assert song.title == "Imported"
            assert song.bpm == 120
            assert len(song.sample_tracks) == 2
            names = [st.name for st in song.sample_tracks]
            assert "kick" in names
            assert "snare" in names

    def test_import_nonexistent_dir(self):
        from code_music import Song

        with self.assertRaises(FileNotFoundError):
            Song.import_stems("/nonexistent/dir")

    def test_import_default_title(self):
        from code_music import Song

        with tempfile.TemporaryDirectory() as tmpdir:
            song = Song.import_stems(tmpdir)
            # Title should be the directory name
            assert song.title == Path(tmpdir).name

    def test_import_custom_bpm(self):
        from code_music import Song

        with tempfile.TemporaryDirectory() as tmpdir:
            song = Song.import_stems(tmpdir, bpm=90)
            assert song.bpm == 90

    def test_import_custom_sample_rate(self):
        from code_music import Song

        with tempfile.TemporaryDirectory() as tmpdir:
            song = Song.import_stems(tmpdir, sample_rate=48000)
            assert song.sample_rate == 48000


# ---------------------------------------------------------------------------
# Metadata embedding
# ---------------------------------------------------------------------------


class TestMetadataEmbedding(unittest.TestCase):
    """Export functions accept metadata parameter."""

    def test_export_mp3_signature_accepts_metadata(self):
        import inspect

        from code_music.export import export_mp3

        sig = inspect.signature(export_mp3)
        assert "metadata" in sig.parameters

    def test_export_flac_signature_accepts_metadata(self):
        import inspect

        from code_music.export import export_flac

        sig = inspect.signature(export_flac)
        assert "metadata" in sig.parameters

    def test_export_ogg_signature_accepts_metadata(self):
        import inspect

        from code_music.export import export_ogg

        sig = inspect.signature(export_ogg)
        assert "metadata" in sig.parameters


# ---------------------------------------------------------------------------
# Round-trip: export_stems -> import_stems
# ---------------------------------------------------------------------------


class TestStemRoundTrip(unittest.TestCase):
    """Export stems then import them back."""

    def test_export_import_round_trip(self):
        from code_music import Note, Song, Track

        song = Song(title="RT Test", bpm=120, sample_rate=22050)
        lead = song.add_track(Track(name="lead", instrument="sine"))
        lead.add(Note("C", 4, 2.0))
        bass = song.add_track(Track(name="bass", instrument="bass"))
        bass.add(Note("C", 2, 2.0))

        with tempfile.TemporaryDirectory() as tmpdir:
            # Export stems
            paths = song.export_stems(tmpdir)
            assert len(paths) == 2

            # Import them back
            imported = Song.import_stems(tmpdir, bpm=120)
            assert len(imported.sample_tracks) == 2
            stem_names = sorted(st.name for st in imported.sample_tracks)
            assert stem_names == ["bass", "lead"]


if __name__ == "__main__":
    unittest.main()
