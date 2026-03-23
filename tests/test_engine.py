"""Tests for core music engine primitives."""

import math

from code_music.engine import (
    Chord,
    Note,
    Song,
    Track,
    midi_to_freq,
    note_name_to_midi,
    scale,
)


class TestFrequency:
    def test_a4_is_440(self):
        assert math.isclose(midi_to_freq(69), 440.0)

    def test_a5_is_880(self):
        assert math.isclose(midi_to_freq(81), 880.0)

    def test_c4_midi(self):
        assert note_name_to_midi("C", 4) == 60

    def test_a4_midi(self):
        assert note_name_to_midi("A", 4) == 69

    def test_sharp(self):
        assert note_name_to_midi("C#", 4) == 61


class TestNote:
    def test_rest_has_no_freq(self):
        r = Note.rest(2.0)
        assert r.freq is None

    def test_a4_freq(self):
        n = Note("A", 4)
        assert math.isclose(n.freq, 440.0)

    def test_midi_int_pitch(self):
        n = Note(pitch=69)
        assert math.isclose(n.freq, 440.0)

    def test_default_duration(self):
        n = Note("C")
        assert n.duration == 1.0

    def test_default_velocity(self):
        n = Note("C")
        assert n.velocity == 0.8


class TestChord:
    def test_major_chord_notes(self):
        c = Chord("C", "maj", 4)
        # C E G -> midi 60, 64, 67
        midis = [n.midi for n in c.notes]
        assert midis == [60, 64, 67]

    def test_minor_chord_notes(self):
        c = Chord("A", "min", 4)
        midis = [n.midi for n in c.notes]
        assert midis == [69, 72, 76]

    def test_maj7(self):
        c = Chord("C", "maj7", 4)
        assert len(c.notes) == 4

    def test_custom_offsets(self):
        c = Chord("C", [0, 7], 4)  # power chord
        midis = [n.midi for n in c.notes]
        assert midis == [60, 67]


class TestScale:
    def test_major_scale_length(self):
        s = scale("C", "major", 4)
        assert len(s) == 7

    def test_pentatonic_length(self):
        s = scale("A", "pentatonic", 4)
        assert len(s) == 5

    def test_custom_length_wraps_octave(self):
        s = scale("C", "major", 4, length=14)
        assert len(s) == 14
        # 15th note (index 7) should be an octave higher than root
        assert s[7].midi == s[0].midi + 12


class TestTrack:
    def test_add_returns_self(self):
        t = Track()
        assert t.add(Note("C")) is t

    def test_total_beats(self):
        t = Track()
        t.add(Note("C", duration=2.0))
        t.add(Note.rest(1.5))
        assert t.total_beats == 3.5

    def test_extend(self):
        t = Track()
        t.extend([Note("C"), Note("D"), Note("E")])
        assert len(t.beats) == 3


class TestSong:
    def test_duration_calculation(self):
        song = Song(bpm=120)
        tr = song.add_track(Track())
        tr.extend([Note("C", duration=4.0)])  # 4 beats @ 120 BPM = 2s
        assert math.isclose(song.duration_sec, 2.0)

    def test_beat_duration_sec(self):
        song = Song(bpm=60)
        assert math.isclose(song.beat_duration_sec, 1.0)
