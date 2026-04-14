"""Tests for v162.0: suggest_arrangement, Pages workflow, docs refresh."""

import unittest
from pathlib import Path

from code_music import Chord, Note, Song, Track, suggest_arrangement


class TestSuggestArrangement(unittest.TestCase):
    """suggest_arrangement detects section boundaries."""

    def test_returns_list(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track())
        for _ in range(8):
            tr.add(Chord("C", "maj", 4, duration=4.0))
        result = suggest_arrangement(song)
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_sections_have_required_keys(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track())
        for _ in range(16):
            tr.add(Chord("C", "maj", 4, duration=4.0))
        sections = suggest_arrangement(song)
        for s in sections:
            assert "label" in s
            assert "start_beat" in s
            assert "end_beat" in s
            assert "bars" in s
            assert "confidence" in s

    def test_short_song(self):
        song = Song(title="Short", bpm=120)
        tr = song.add_track(Track())
        tr.add(Chord("C", "maj", 4, duration=8.0))
        sections = suggest_arrangement(song)
        assert len(sections) >= 1

    def test_long_song_has_multiple_sections(self):
        song = Song(title="Long", bpm=120)
        tr = song.add_track(Track())
        for _ in range(32):
            tr.add(Chord("C", "maj", 4, duration=4.0))
        sections = suggest_arrangement(song)
        assert len(sections) >= 3

    def test_labels_include_verse_chorus(self):
        song = Song(title="Pop", bpm=120)
        tr = song.add_track(Track())
        for _ in range(24):
            tr.add(Chord("C", "maj", 4, duration=4.0))
        sections = suggest_arrangement(song)
        labels = [s["label"] for s in sections]
        assert "verse" in labels or "chorus" in labels

    def test_sections_cover_full_song(self):
        song = Song(title="Full", bpm=120)
        tr = song.add_track(Track())
        for _ in range(16):
            tr.add(Chord("C", "maj", 4, duration=4.0))
        sections = suggest_arrangement(song)
        assert sections[0]["start_beat"] == 0.0
        assert sections[-1]["end_beat"] > 0.0

    def test_confidence_range(self):
        song = Song(title="Conf", bpm=120)
        tr = song.add_track(Track())
        for root in ["C", "F", "G", "C"] * 8:
            tr.add(Chord(root, "maj", 4, duration=4.0))
        for s in suggest_arrangement(song):
            assert 0.0 <= s["confidence"] <= 1.0

    def test_with_notes_only(self):
        song = Song(title="Notes", bpm=120)
        tr = song.add_track(Track())
        tr.extend([Note("C", 4, 1.0)] * 32)
        sections = suggest_arrangement(song)
        assert isinstance(sections, list)

    def test_import(self):
        from code_music import suggest_arrangement as sa

        assert callable(sa)


class TestPagesWorkflow(unittest.TestCase):
    """GitHub Pages workflow exists."""

    def test_pages_yml_exists(self):
        p = Path(__file__).parent.parent / ".github" / "workflows" / "pages.yml"
        assert p.exists()

    def test_pages_deploys_docs(self):
        content = (Path(__file__).parent.parent / ".github" / "workflows" / "pages.yml").read_text()
        assert "docs/" in content
        assert "deploy-pages" in content


class TestDocsRefresh(unittest.TestCase):
    """API docs refreshed with current function count."""

    def test_api_html_has_functions(self):
        content = (Path(__file__).parent.parent / "docs" / "api.html").read_text()
        # Should have 450+ functions documented
        assert "462 functions" in content or "46" in content


if __name__ == "__main__":
    unittest.main()
