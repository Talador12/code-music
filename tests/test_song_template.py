"""Tests for v99.0 — SongTemplate."""

from code_music.engine import Note
from code_music.theory import SongTemplate


class TestSongTemplate:
    def test_pop_form(self):
        t = SongTemplate("pop")
        assert len(t.sections) == 8

    def test_fill_and_render(self):
        t = SongTemplate("aaba")
        t.fill("A", chords=[("C", "maj")])
        t.fill("B", chords=[("G", "dom7")])
        result = t.render()
        assert len(result["chords"]) == 4  # A, A, B, A → 4 chords

    def test_render_with_melody(self):
        t = SongTemplate("blues")
        t.fill("head", melody=[Note("E", 5, 1.0)])
        t.fill("solo", melody=[Note("G", 5, 1.0)])
        result = t.render()
        assert len(result["melody"]) == 3  # head, solo, head

    def test_empty_render(self):
        t = SongTemplate("aaba")
        result = t.render()
        assert result["chords"] == []
        assert result["form"] == ["A", "A", "B", "A"]

    def test_randomize(self):
        t = SongTemplate("pop")
        t.randomize(key="C", seed=42)
        result = t.render()
        assert len(result["chords"]) > 0
        assert len(result["melody"]) > 0

    def test_chaining(self):
        t = SongTemplate("aaba")
        result = t.fill("A", chords=[("C", "maj")]).fill("B", chords=[("F", "maj")]).render()
        assert len(result["chords"]) == 4

    def test_randomize_deterministic(self):
        a = SongTemplate("pop").randomize(seed=99).render()
        b = SongTemplate("pop").randomize(seed=99).render()
        assert a["chords"] == b["chords"]
