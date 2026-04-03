"""Tests for arpeggiate_chord, staccato, legato_connect."""

from code_music import Note
from code_music.theory import arpeggiate_chord, legato_connect, staccato


class TestArpeggiateChord:
    def test_up(self):
        a = arpeggiate_chord("C", "maj", direction="up")
        assert a[0].pitch == "C"
        assert len(a) == 3

    def test_down(self):
        a = arpeggiate_chord("C", "maj", direction="down")
        assert a[0].pitch == "G"

    def test_updown(self):
        a = arpeggiate_chord("C", "maj7", direction="updown")
        assert len(a) > 4

    def test_repeats(self):
        a = arpeggiate_chord("C", "maj", repeats=2)
        assert len(a) == 6

    def test_unknown_raises(self):
        import pytest

        with pytest.raises(ValueError):
            arpeggiate_chord("C", "imaginary")


class TestStaccato:
    def test_basic(self):
        notes = [Note("C", 4, 1.0)]
        s = staccato(notes, ratio=0.5)
        assert s[0].duration == 0.5
        assert s[1].pitch is None  # rest

    def test_rests_preserved(self):
        s = staccato([Note.rest(1.0)])
        assert s[0].pitch is None

    def test_total_duration(self):
        notes = [Note("C", 4, 1.0)]
        s = staccato(notes, ratio=0.5)
        total = sum(n.duration for n in s)
        assert abs(total - 1.0) < 0.01


class TestLegatoConnect:
    def test_extends(self):
        notes = [Note("C", 4, 1.0)]
        result = legato_connect(notes, overlap=0.2)
        assert result[0].duration == 1.2

    def test_rests(self):
        result = legato_connect([Note.rest(1.0)])
        assert result[0].pitch is None and result[0].duration == 1.0

    def test_preserves_pitch(self):
        result = legato_connect([Note("E", 5, 0.5)])
        assert result[0].pitch == "E"
