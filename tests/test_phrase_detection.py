"""Tests for v98.0 — detect_phrases, phrase_lengths."""

from code_music.engine import Note
from code_music.theory import detect_phrases, phrase_lengths


class TestDetectPhrases:
    def test_single_phrase(self):
        notes = [Note("C", 5, 1.0)] * 4
        phrases = detect_phrases(notes)
        assert len(phrases) == 1
        assert phrases[0]["length"] == 3  # end idx - start idx

    def test_two_phrases(self):
        notes = [Note("C", 5, 1.0), Note("D", 5, 1.0), Note.rest(1.0), Note("E", 5, 1.0)]
        phrases = detect_phrases(notes, min_gap=0.5)
        assert len(phrases) == 2

    def test_empty(self):
        assert detect_phrases([]) == []

    def test_start_end_positions(self):
        notes = [Note("C", 5, 1.0), Note.rest(1.0), Note("E", 5, 1.0)]
        phrases = detect_phrases(notes, min_gap=0.5)
        assert phrases[0]["start"] == 0
        assert phrases[0]["end"] == 1


class TestPhraseLengths:
    def test_returns_lengths(self):
        notes = [Note("C", 5, 1.0)] * 3 + [Note.rest(1.0)] + [Note("E", 5, 1.0)] * 2
        lengths = phrase_lengths(notes, min_gap=0.5)
        assert lengths[0] == 3

    def test_single_phrase(self):
        notes = [Note("C", 5, 1.0)] * 5
        lengths = phrase_lengths(notes)
        assert len(lengths) == 1
        assert lengths[0] > 0
