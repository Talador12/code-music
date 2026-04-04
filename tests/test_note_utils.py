"""Tests for v114.0 — note_to_midi, midi_to_note, note_to_freq."""

from code_music.theory import midi_to_note, note_to_freq, note_to_midi


class TestNoteToMidi:
    def test_middle_c(self):
        assert note_to_midi("C", 4) == 60

    def test_a4(self):
        assert note_to_midi("A", 4) == 69

    def test_c0(self):
        assert note_to_midi("C", -1) == 0


class TestMidiToNote:
    def test_60(self):
        assert midi_to_note(60) == ("C", 4)

    def test_69(self):
        assert midi_to_note(69) == ("A", 4)

    def test_round_trip(self):
        for midi in [48, 60, 72, 84]:
            pitch, octave = midi_to_note(midi)
            assert note_to_midi(pitch, octave) == midi


class TestNoteToFreq:
    def test_a4(self):
        assert note_to_freq("A", 4) == 440.0

    def test_a5(self):
        assert abs(note_to_freq("A", 5) - 880.0) < 0.1

    def test_middle_c(self):
        freq = note_to_freq("C", 4)
        assert 261 < freq < 262  # C4 ≈ 261.63 Hz

    def test_custom_tuning(self):
        freq = note_to_freq("A", 4, a4=432.0)
        assert freq == 432.0
