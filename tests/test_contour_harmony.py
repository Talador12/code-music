"""Tests for melody_contour, harmonic_rhythm, consonance_score."""

from code_music import Chord, Note, Song, Track
from code_music.theory import consonance_score, harmonic_rhythm, melody_contour

SR = 22050


class TestMelodyContour:
    def test_ascending(self):
        notes = [Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0), Note("C", 5, 1.0)]
        c = melody_contour(notes)
        assert c["direction"] == "ascending"

    def test_descending(self):
        notes = [Note("C", 5, 1.0), Note("G", 4, 1.0), Note("E", 4, 1.0), Note("C", 4, 1.0)]
        c = melody_contour(notes)
        assert c["direction"] == "descending"

    def test_step_count(self):
        notes = [Note("C", 4, 1.0), Note("D", 4, 1.0)]
        c = melody_contour(notes)
        assert c["steps"] == 1

    def test_contour_string(self):
        notes = [Note("C", 4, 1.0), Note("E", 4, 1.0), Note("D", 4, 1.0)]
        c = melody_contour(notes)
        assert "+" in c["contour_string"] and "-" in c["contour_string"]

    def test_single_note(self):
        c = melody_contour([Note("C", 4, 1.0)])
        assert c["direction"] == "static"


class TestHarmonicRhythm:
    def test_basic(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="pad", instrument="pad")).extend(
            [Chord("C", "maj", 3, duration=4.0), Chord("G", "maj", 3, duration=4.0)]
        )
        h = harmonic_rhythm(song)
        assert h["total_chords"] == 2
        assert h["changes_per_bar"] > 0

    def test_no_chords(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 4.0))
        h = harmonic_rhythm(song)
        assert h["total_chords"] == 0


class TestConsonanceScore:
    def test_octave(self):
        notes = [Note("C", 4, 1.0), Note("C", 5, 1.0)]
        assert consonance_score(notes) == 1.0

    def test_fifth(self):
        notes = [Note("C", 4, 1.0), Note("G", 4, 1.0)]
        assert consonance_score(notes) == 0.9

    def test_tritone_low(self):
        notes = [Note("C", 4, 1.0), Note("F#", 4, 1.0)]
        assert consonance_score(notes) < 0.5

    def test_single_note(self):
        assert consonance_score([Note("C", 4, 1.0)]) == 1.0
