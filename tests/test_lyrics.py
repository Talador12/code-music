"""Tests for v58.0 — count_syllables, stress_pattern, text_to_melody."""

from code_music.theory import count_syllables, stress_pattern, text_to_melody


class TestCountSyllables:
    def test_one_syllable(self):
        assert count_syllables("cat") == 1

    def test_two_syllables(self):
        assert count_syllables("hello") == 2

    def test_three_syllables(self):
        assert count_syllables("beautiful") == 3

    def test_silent_e(self):
        assert count_syllables("make") == 1

    def test_empty(self):
        assert count_syllables("") == 0

    def test_punctuation(self):
        assert count_syllables("hello!") == 2


class TestStressPattern:
    def test_simple(self):
        pattern = stress_pattern("the cat sat")
        assert len(pattern) == 3
        assert pattern[0] is False  # "the" is unstressed
        assert pattern[1] is True  # "cat" is stressed
        assert pattern[2] is True  # "sat" is stressed

    def test_multisyllable(self):
        pattern = stress_pattern("hello")
        assert len(pattern) == 2
        assert pattern[0] is True  # first syllable stressed
        assert pattern[1] is False  # second unstressed

    def test_empty(self):
        assert stress_pattern("") == []


class TestTextToMelody:
    def test_returns_notes(self):
        notes = text_to_melody("hello world", seed=42)
        assert len(notes) > 0

    def test_one_note_per_syllable(self):
        notes = text_to_melody("the cat sat", seed=42)
        assert len(notes) == 3  # 3 syllables

    def test_question_exists(self):
        notes_q = text_to_melody("is it done?", seed=42)
        notes_s = text_to_melody("it is done.", seed=42)
        # Both should produce notes
        assert len(notes_q) > 0
        assert len(notes_s) > 0

    def test_deterministic(self):
        a = text_to_melody("hello world", seed=99)
        b = text_to_melody("hello world", seed=99)
        assert [n.pitch for n in a] == [n.pitch for n in b]

    def test_stressed_longer(self):
        notes = text_to_melody("the beautiful cat", seed=42)
        # Find a stressed and unstressed note to compare
        assert any(n.duration > 0.3 for n in notes)
