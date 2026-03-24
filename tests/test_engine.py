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
    def test_major_scale_one_octave(self):
        # Default octaves=1: 7 intervals + top root = 8 notes
        s = scale("C", "major", 4)
        assert len(s) == 8
        assert s[0].midi == 60  # C4
        assert s[-1].midi == 72  # C5

    def test_pentatonic_one_octave(self):
        s = scale("A", "pentatonic", 4)
        assert len(s) == 6  # 5 intervals + top root
        assert s[-1].midi == s[0].midi + 12

    def test_two_octaves(self):
        s = scale("C", "major", 4, octaves=2)
        assert len(s) == 15  # 7*2 + 1 top root
        assert s[-1].midi == 60 + 24  # C6

    def test_three_octaves(self):
        s = scale("C", "minor", 4, octaves=3)
        assert len(s) == 22  # 7*3 + 1
        assert s[-1].midi == 60 + 36  # C7

    def test_chromatic_one_octave(self):
        s = scale("C", "chromatic", 4)
        assert len(s) == 13  # 12 semitones + top root

    def test_pentatonic_two_octaves(self):
        s = scale("A", "pentatonic", 4, octaves=2)
        assert len(s) == 11  # 5*2 + 1

    def test_explicit_length_overrides_octaves(self):
        s = scale("C", "major", 4, length=7)
        assert len(s) == 7
        s14 = scale("C", "major", 4, length=14)
        assert len(s14) == 14
        assert s14[7].midi == s14[0].midi + 12

    def test_top_root_is_octave_above(self):
        for mode in ["major", "minor", "dorian", "pentatonic", "blues"]:
            s = scale("D", mode, 4)
            assert s[-1].midi == s[0].midi + 12, f"failed for {mode}"


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


class TestChordVoicing:
    def test_spread_widens_range(self):
        c = Chord("C", "maj7", 4)
        close_range = c.notes[-1].midi - c.notes[0].midi
        spread_range = c.spread().notes[-1].midi - c.spread().notes[0].midi
        assert spread_range > close_range

    def test_spread_preserves_note_count(self):
        c = Chord("A", "min9", 3)
        assert len(c.spread().notes) == len(c.notes)

    def test_drop2_different_from_close(self):
        c = Chord("C", "maj7", 4)
        close_midis = [n.midi for n in c.notes]
        drop2_midis = [n.midi for n in c.drop2().notes]
        assert close_midis != drop2_midis

    def test_drop2_preserves_note_count(self):
        c = Chord("G", "dom7", 3)
        assert len(c.drop2().notes) == len(c.notes)

    def test_close_compacts_to_octave(self):
        c = Chord("C", "maj7", 4)
        closed = c.spread(2).close()
        midis = [n.midi for n in closed.notes]
        assert max(midis) - min(midis) <= 12

    def test_spread_default_one_octave(self):
        c = Chord("C", "maj", 4)
        spread_midis = sorted(n.midi for n in c.spread().notes)
        close_midis = sorted(n.midi for n in c.notes)
        # Spread voicing should have a wider total range than close
        spread_range = spread_midis[-1] - spread_midis[0]
        close_range = close_midis[-1] - close_midis[0]
        assert spread_range > close_range

    def test_triad_drop2_handles_small_chord(self):
        c = Chord("C", "maj", 4)
        d2 = c.drop2()
        assert len(d2.notes) == 3  # should not crash on 3-note chord

    def test_two_note_chord_drop2_passthrough(self):
        c = Chord("C", "power", 4)  # [0, 7] — only 2 notes
        d2 = c.drop2()
        assert len(d2.notes) == 2  # should not crash

    def test_spread_preserves_duration_velocity(self):
        c = Chord("D", "min7", 3, duration=3.0, velocity=0.42)
        s = c.spread()
        assert s.duration == 3.0
        assert s.velocity == 0.42


class TestTimeSigAutomation:
    def test_add_time_sig_change(self):
        song = Song(bpm=120, time_sig=(4, 4))
        song.add_time_sig_change(16.0, 3, 4)
        assert len(song.time_sig_map) == 1
        assert song.time_sig_map[0] == (16.0, 3, 4)

    def test_multiple_changes_sorted(self):
        song = Song(bpm=120, time_sig=(4, 4))
        song.add_time_sig_change(32.0, 7, 8)
        song.add_time_sig_change(16.0, 3, 4)
        assert song.time_sig_map[0][0] == 16.0
        assert song.time_sig_map[1][0] == 32.0

    def test_time_sig_at_default(self):
        song = Song(bpm=120, time_sig=(4, 4))
        assert song.time_sig_at(0.0) == (4, 4)
        assert song.time_sig_at(100.0) == (4, 4)

    def test_time_sig_at_after_change(self):
        song = Song(bpm=120, time_sig=(4, 4))
        song.add_time_sig_change(16.0, 3, 4)
        assert song.time_sig_at(0.0) == (4, 4)
        assert song.time_sig_at(15.9) == (4, 4)
        assert song.time_sig_at(16.0) == (3, 4)
        assert song.time_sig_at(100.0) == (3, 4)

    def test_time_sig_at_multiple_changes(self):
        song = Song(bpm=120, time_sig=(4, 4))
        song.add_time_sig_change(8.0, 3, 4)
        song.add_time_sig_change(20.0, 7, 8)
        song.add_time_sig_change(30.0, 6, 8)
        assert song.time_sig_at(5.0) == (4, 4)
        assert song.time_sig_at(10.0) == (3, 4)
        assert song.time_sig_at(25.0) == (7, 8)
        assert song.time_sig_at(35.0) == (6, 8)

    def test_chaining(self):
        song = Song(bpm=120)
        result = song.add_time_sig_change(8.0, 3, 4)
        assert result is song  # returns self for chaining
