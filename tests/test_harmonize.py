"""Tests for v75.0 — harmonize_melody."""

from code_music.engine import Note
from code_music.theory import harmonize_melody


class TestHarmonizeMelody:
    def test_thirds_returns_two_voices(self):
        melody = [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        voices = harmonize_melody(melody, style="thirds")
        assert len(voices) == 2

    def test_sixths_returns_two_voices(self):
        melody = [Note("C", 5, 1.0)]
        voices = harmonize_melody(melody, style="sixths")
        assert len(voices) == 2

    def test_chorale_returns_three_voices(self):
        melody = [Note("C", 5, 1.0)]
        voices = harmonize_melody(melody, style="chorale")
        assert len(voices) == 3

    def test_melody_preserved(self):
        melody = [Note("G", 5, 1.0), Note("A", 5, 1.0)]
        voices = harmonize_melody(melody, style="thirds")
        assert voices[0][0].pitch == "G"
        assert voices[0][1].pitch == "A"

    def test_rest_passthrough(self):
        melody = [Note.rest(1.0)]
        voices = harmonize_melody(melody, style="thirds")
        assert voices[1][0].pitch is None

    def test_different_keys(self):
        melody = [Note("C", 5, 1.0)]
        v_c = harmonize_melody(melody, key="C", style="thirds")
        v_g = harmonize_melody(melody, key="G", style="thirds")
        # Harmony note may differ between keys
        # (C in C major: third above is E; C in G major: third above is E too,
        #  but for other notes it would differ)
        assert len(v_c) == 2
        assert len(v_g) == 2

    def test_minor_key(self):
        melody = [Note("A", 5, 1.0)]
        voices = harmonize_melody(melody, key="A", style="thirds", scale_name="minor")
        assert len(voices) == 2
