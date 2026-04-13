"""Tests for v138.0: REPL, API docs generator, CLI --repl flag."""

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

# ---------------------------------------------------------------------------
# REPL module
# ---------------------------------------------------------------------------


class TestREPLModule(unittest.TestCase):
    """REPL module imports and slash command handling."""

    def test_import_repl(self):
        from code_music.repl import start_repl

        assert callable(start_repl)

    def test_import_music_console(self):
        from code_music.repl import MusicConsole

        assert MusicConsole is not None

    def test_handle_slash_help(self):
        from code_music.repl import _handle_slash_command

        ns = {}
        result = _handle_slash_command("/help", ns)
        assert result is True

    def test_handle_slash_info_no_song(self):
        from code_music.repl import _handle_slash_command

        ns = {"song": None}
        out = io.StringIO()
        with redirect_stdout(out):
            result = _handle_slash_command("/info", ns)
        assert result is True

    def test_handle_slash_info_with_song(self):
        from code_music import Song
        from code_music.repl import _handle_slash_command

        song = Song(title="Test", bpm=120)
        ns = {"song": song}
        out = io.StringIO()
        with redirect_stdout(out):
            _handle_slash_command("/info", ns)
        assert "Test" in out.getvalue() or "120" in out.getvalue()

    def test_handle_slash_tracks_empty(self):
        from code_music import Song
        from code_music.repl import _handle_slash_command

        ns = {"song": Song(title="Test", bpm=120)}
        out = io.StringIO()
        with redirect_stdout(out):
            _handle_slash_command("/tracks", ns)
        assert "no tracks" in out.getvalue()

    def test_handle_slash_tracks_with_data(self):
        from code_music import Note, Song, Track
        from code_music.repl import _handle_slash_command

        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("C", 4, 1.0))
        ns = {"song": song}
        out = io.StringIO()
        with redirect_stdout(out):
            _handle_slash_command("/tracks", ns)
        assert "lead" in out.getvalue()
        assert "piano" in out.getvalue()

    def test_handle_slash_reset(self):
        from code_music import Song, Track
        from code_music.repl import _handle_slash_command

        song = Song(title="Old", bpm=90)
        song.add_track(Track())
        ns = {"song": song}
        out = io.StringIO()
        with redirect_stdout(out):
            _handle_slash_command("/reset", ns)
        assert ns["song"].title == "REPL Session"
        assert len(ns["song"].tracks) == 0

    def test_handle_slash_bpm_get(self):
        from code_music import Song
        from code_music.repl import _handle_slash_command

        ns = {"song": Song(title="Test", bpm=140)}
        out = io.StringIO()
        with redirect_stdout(out):
            _handle_slash_command("/bpm", ns)
        assert "140" in out.getvalue()

    def test_handle_slash_bpm_set(self):
        from code_music import Song
        from code_music.repl import _handle_slash_command

        song = Song(title="Test", bpm=120)
        ns = {"song": song}
        out = io.StringIO()
        with redirect_stdout(out):
            _handle_slash_command("/bpm 90", ns)
        assert song.bpm == 90

    def test_handle_slash_undo(self):
        from code_music import Song, Track
        from code_music.repl import _handle_slash_command

        song = Song(title="Test", bpm=120)
        song.add_track(Track(name="a"))
        song.add_track(Track(name="b"))
        ns = {"song": song}
        out = io.StringIO()
        with redirect_stdout(out):
            _handle_slash_command("/undo", ns)
        assert len(song.tracks) == 1
        assert song.tracks[0].name == "a"

    def test_handle_unknown_command(self):
        from code_music.repl import _handle_slash_command

        ns = {}
        out = io.StringIO()
        with redirect_stdout(out):
            result = _handle_slash_command("/nonexistent", ns)
        assert result is True
        assert "Unknown" in out.getvalue()

    def test_non_slash_not_handled(self):
        from code_music.repl import _handle_slash_command

        result = _handle_slash_command("not a command", {})
        assert result is False

    def test_handle_slash_quit(self):
        from code_music.repl import _handle_slash_command

        with self.assertRaises(SystemExit):
            _handle_slash_command("/quit", {})


# ---------------------------------------------------------------------------
# CLI --repl flag
# ---------------------------------------------------------------------------


class TestCLIRepl(unittest.TestCase):
    """CLI accepts --repl flag."""

    def test_repl_in_help(self):
        from code_music.cli import main

        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                main(["--help"])
            except SystemExit:
                pass
        combined = out.getvalue() + err.getvalue()
        assert "repl" in combined.lower()


# ---------------------------------------------------------------------------
# API docs generator
# ---------------------------------------------------------------------------


class TestAPIDocs(unittest.TestCase):
    """API reference generator produces valid output."""

    def test_docs_api_html_exists(self):
        """docs/api.html should exist after generation."""
        api_path = Path(__file__).parent.parent / "docs" / "api.html"
        assert api_path.exists(), "docs/api.html not found - run: python scripts/build_api_docs.py"

    def test_docs_contains_functions(self):
        """api.html should contain known function names."""
        api_path = Path(__file__).parent.parent / "docs" / "api.html"
        if not api_path.exists():
            self.skipTest("docs/api.html not generated")
        content = api_path.read_text()
        for name in ["generate_form", "style_fingerprint", "progression_dna", "compose"]:
            assert name in content, f"{name} not found in api.html"

    def test_docs_contains_categories(self):
        """api.html should have module categories."""
        api_path = Path(__file__).parent.parent / "docs" / "api.html"
        if not api_path.exists():
            self.skipTest("docs/api.html not generated")
        content = api_path.read_text()
        for cat in ["Harmony", "Generation", "Analysis", "Engine"]:
            assert cat in content, f"Category {cat} not found in api.html"

    def test_docs_valid_html(self):
        """api.html should be valid HTML (has doctype, html, body tags)."""
        api_path = Path(__file__).parent.parent / "docs" / "api.html"
        if not api_path.exists():
            self.skipTest("docs/api.html not generated")
        content = api_path.read_text()
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "</html>" in content
        assert "<body>" in content

    def test_docs_search_functionality(self):
        """api.html should have search input."""
        api_path = Path(__file__).parent.parent / "docs" / "api.html"
        if not api_path.exists():
            self.skipTest("docs/api.html not generated")
        content = api_path.read_text()
        assert 'id="search"' in content

    def test_generator_script_runs(self):
        """build_api_docs.py should be importable and callable."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "build_api_docs",
            str(Path(__file__).parent.parent / "scripts" / "build_api_docs.py"),
        )
        assert spec is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert callable(getattr(mod, "build_api_docs", None))


if __name__ == "__main__":
    unittest.main()
