"""Tests for canon, hocket, sequence_by_interval."""

from code_music import Note
from code_music.theory import canon, hocket, sequence_by_interval


class TestCanon:
    def test_two_voices(self):
        melody = [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        voices = canon(melody, delay_beats=2.0, voices=2)
        assert len(voices) == 2
        assert voices[0][0].pitch == "C"  # no delay
        assert voices[1][0].pitch is None  # rest (delay)

    def test_three_voices(self):
        melody = [Note("C", 5, 1.0)]
        voices = canon(melody, voices=3)
        assert len(voices) == 3

    def test_preserves_melody(self):
        melody = [Note("A", 4, 0.5), Note("B", 4, 0.5)]
        voices = canon(melody)
        assert voices[0][:2] == melody  # first voice = original


class TestHocket:
    def test_two_voices(self):
        melody = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0), Note("B", 5, 1.0)]
        voices = hocket(melody, voices=2)
        assert len(voices) == 2
        assert voices[0][0].pitch == "C"
        assert voices[0][1].pitch is None  # rest
        assert voices[1][0].pitch is None  # rest
        assert voices[1][1].pitch == "E"

    def test_three_voices(self):
        melody = [Note("C", 5, 1.0)] * 6
        voices = hocket(melody, voices=3)
        assert len(voices) == 3
        for v in voices:
            assert len(v) == 6

    def test_preserves_total(self):
        melody = [Note("C", 5, 1.0)] * 4
        voices = hocket(melody)
        pitched = sum(1 for v in voices for n in v if n.pitch is not None)
        assert pitched == 4


class TestSequenceByInterval:
    def test_basic(self):
        melody = [Note("C", 5, 0.5), Note("E", 5, 0.5)]
        s = sequence_by_interval(melody, interval=2, repetitions=3)
        assert len(s) == 6
        assert s[0].pitch == "C"
        assert s[2].pitch == "D"  # up 2 semitones

    def test_single_rep(self):
        melody = [Note("C", 5, 1.0)]
        s = sequence_by_interval(melody, repetitions=1)
        assert len(s) == 1

    def test_rests_preserved(self):
        melody = [Note.rest(1.0), Note("C", 5, 1.0)]
        s = sequence_by_interval(melody, repetitions=2)
        assert s[0].pitch is None
