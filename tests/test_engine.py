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


class TestSongMerge:
    def test_merge_combines_tracks(self):
        s1 = Song(bpm=120)
        s1.add_track(Track(name="drums", instrument="drums_kick"))
        s2 = Song(bpm=120)
        s2.add_track(Track(name="melody", instrument="piano"))
        merged = s1.merge(s2)
        assert len(merged.tracks) == 2
        assert merged.tracks[0].name == "drums"
        assert merged.tracks[1].name == "melody"

    def test_merge_uses_first_bpm(self):
        s1 = Song(bpm=120)
        s2 = Song(bpm=140)
        merged = s1.merge(s2)
        assert merged.bpm == 120

    def test_merge_default_title(self):
        s1 = Song(title="A", bpm=120)
        s2 = Song(title="B", bpm=120)
        merged = s1.merge(s2)
        assert "A" in merged.title and "B" in merged.title

    def test_merge_custom_title(self):
        s1 = Song(title="A", bpm=120)
        s2 = Song(title="B", bpm=120)
        merged = s1.merge(s2, title="Combined")
        assert merged.title == "Combined"

    def test_merge_preserves_notes(self):
        s1 = Song(bpm=120)
        t1 = s1.add_track(Track())
        t1.add(Note("C", 4, 1.0))
        s2 = Song(bpm=120)
        t2 = s2.add_track(Track())
        t2.add(Note("G", 5, 2.0))
        merged = s1.merge(s2)
        assert merged.tracks[0].beats[0].event.pitch == "C"
        assert merged.tracks[1].beats[0].event.pitch == "G"

    def test_merge_does_not_mutate_originals(self):
        s1 = Song(bpm=120)
        s1.add_track(Track(name="a"))
        s2 = Song(bpm=120)
        s2.add_track(Track(name="b"))
        merged = s1.merge(s2)
        assert len(s1.tracks) == 1  # original unchanged
        assert len(s2.tracks) == 1
        assert len(merged.tracks) == 2

    def test_merge_renders(self):
        import numpy as np

        from code_music.synth import Synth
        s1 = Song(bpm=120, sample_rate=22050)
        t1 = s1.add_track(Track(instrument="sine"))
        t1.add(Note("C", 4, 1.0))
        s2 = Song(bpm=120, sample_rate=22050)
        t2 = s2.add_track(Track(instrument="piano"))
        t2.add(Note("G", 5, 1.0))
        merged = s1.merge(s2)
        samples = Synth(22050).render_song(merged)
        assert np.max(np.abs(samples)) > 0.1


class TestTrackReverse:
    def test_reverse_reverses_notes(self):
        t = Track()
        t.add(Note("C", 4, 1.0))
        t.add(Note("E", 4, 1.0))
        t.add(Note("G", 4, 1.0))
        rev = t.reverse()
        pitches = [b.event.pitch for b in rev.beats]
        assert pitches == ["G", "E", "C"]

    def test_reverse_preserves_instrument(self):
        t = Track(name="mel", instrument="piano", volume=0.5, pan=-0.3)
        t.add(Note("C", 4, 1.0))
        rev = t.reverse()
        assert rev.instrument == "piano"
        assert rev.volume == 0.5
        assert rev.pan == -0.3

    def test_reverse_preserves_total_beats(self):
        t = Track()
        t.add(Note("C", 4, 2.0))
        t.add(Note("E", 4, 1.0))
        t.add(Note("G", 4, 3.0))
        rev = t.reverse()
        assert rev.total_beats == t.total_beats

    def test_reverse_does_not_mutate_original(self):
        t = Track()
        t.add(Note("C", 4, 1.0))
        t.add(Note("G", 4, 1.0))
        rev = t.reverse()
        assert t.beats[0].event.pitch == "C"
        assert rev.beats[0].event.pitch == "G"

    def test_reverse_empty_track(self):
        t = Track()
        rev = t.reverse()
        assert len(rev.beats) == 0


class TestChordVoicings:
    def test_returns_dict(self):
        v = Chord("C", "maj7", 4).voicings()
        assert isinstance(v, dict)

    def test_all_keys_present(self):
        v = Chord("C", "maj7", 4).voicings()
        for key in ("root", "inv1", "inv2", "drop2", "spread", "close", "shell"):
            assert key in v, f"missing key: {key}"

    def test_all_values_are_chords(self):
        v = Chord("A", "min7", 3).voicings()
        for key, chord in v.items():
            assert isinstance(chord, Chord), f"{key} is not a Chord"

    def test_root_is_unchanged(self):
        c = Chord("G", "dom7", 3, duration=2.0, velocity=0.6)
        v = c.voicings()
        assert v["root"] is c

    def test_shell_has_three_notes_for_seventh(self):
        v = Chord("C", "maj7", 4).voicings()
        assert len(v["shell"].notes) == 3  # root + 3rd + 7th

    def test_shell_has_two_notes_for_triad(self):
        v = Chord("C", "maj", 4).voicings()
        assert len(v["shell"].notes) == 2  # root + 3rd

    def test_voicings_differ(self):
        v = Chord("D", "min7", 3).voicings()
        midis = {}
        for key, chord in v.items():
            midis[key] = tuple(sorted(n.midi for n in chord.notes))
        # At least some voicings should differ from root
        unique = set(midis.values())
        assert len(unique) > 1, "all voicings produced identical notes"

    def test_all_voicings_render(self):
        import numpy as np

        from code_music.synth import Synth
        for key, chord in Chord("F", "maj7", 3, duration=1.0).voicings().items():
            song = Song(bpm=120, sample_rate=22050)
            tr = song.add_track(Track(instrument="piano"))
            tr.add(chord)
            samples = Synth(22050).render_song(song)
            assert np.max(np.abs(samples)) > 0.0, f"voicing '{key}' produced silence"


class TestSongInfo:
    def test_returns_dict(self):
        s = Song(title="Test", bpm=120)
        assert isinstance(s.info(), dict)

    def test_contains_all_keys(self):
        s = Song(title="Test", bpm=120)
        info = s.info()
        for key in ("title", "bpm", "duration_sec", "total_beats", "time_sig",
                     "key_sig", "composer", "sample_rate", "tracks",
                     "poly_tracks", "voice_tracks", "track_names"):
            assert key in info, f"missing key: {key}"

    def test_title_and_bpm(self):
        s = Song(title="My Song", bpm=140)
        info = s.info()
        assert info["title"] == "My Song"
        assert info["bpm"] == 140.0

    def test_track_count(self):
        s = Song(bpm=120)
        s.add_track(Track(name="drums"))
        s.add_track(Track(name="bass"))
        info = s.info()
        assert info["tracks"] == 2
        assert info["track_names"] == ["drums", "bass"]

    def test_duration_with_notes(self):
        s = Song(bpm=120)
        tr = s.add_track(Track())
        tr.add(Note("C", 4, 4.0))
        info = s.info()
        assert info["duration_sec"] > 0
        assert info["total_beats"] == 4.0

    def test_time_sig_and_key(self):
        s = Song(bpm=120, time_sig=(3, 4), key_sig="Bb")
        info = s.info()
        assert info["time_sig"] == (3, 4)
        assert info["key_sig"] == "Bb"


class TestShellVoicing:
    def test_seventh_chord_three_notes(self):
        c = Chord("C", "maj7", 3)
        sh = c.shell_voicing()
        assert len(sh.notes) == 3

    def test_triad_two_notes(self):
        c = Chord("C", "maj", 3)
        sh = c.shell_voicing()
        assert len(sh.notes) == 2

    def test_preserves_duration_velocity(self):
        c = Chord("D", "min7", 3, duration=3.0, velocity=0.42)
        sh = c.shell_voicing()
        assert sh.duration == 3.0
        assert sh.velocity == 0.42

    def test_bass_override_adds_note(self):
        c = Chord("C", "maj7", 3)
        sh = c.shell_voicing(bass="E")
        # bass + shell = 4 notes
        assert len(sh.notes) == 4

    def test_bass_override_lowest_note(self):
        c = Chord("C", "maj7", 4)
        sh = c.shell_voicing(bass="E", bass_octave=2)
        midis = sorted(n.midi for n in sh.notes)
        # E2 = midi 40, should be the lowest
        assert midis[0] == 40

    def test_no_bass_root_is_lowest(self):
        c = Chord("G", "dom7", 3)
        sh = c.shell_voicing()
        midis = sorted(n.midi for n in sh.notes)
        # Root G3 = midi 55 should be in there
        assert 55 in midis

    def test_renders_without_error(self):
        import numpy as np

        from code_music.synth import Synth
        song = Song(bpm=120, sample_rate=22050)
        tr = song.add_track(Track(instrument="piano"))
        tr.add(Chord("A", "min7", 3, duration=2.0).shell_voicing())
        tr.add(Chord("D", "dom7", 3, duration=2.0).shell_voicing(bass="F#"))
        samples = Synth(22050).render_song(song)
        assert np.max(np.abs(samples)) > 0.0


class TestTrackQuantize:
    def test_snaps_to_grid(self):
        t = Track()
        t.add(Note("C", 4, 0.33))   # ~1/3 beat
        t.add(Note("E", 4, 0.78))   # ~3/4 beat
        q = t.quantize(grid=0.25)
        assert q.beats[0].event.duration == 0.25  # snapped to 0.25
        assert q.beats[1].event.duration == 0.75  # snapped to 0.75

    def test_preserves_pitch(self):
        t = Track()
        t.add(Note("G", 5, 0.33))
        q = t.quantize(grid=0.5)
        assert q.beats[0].event.pitch == "G"
        assert q.beats[0].event.octave == 5

    def test_minimum_duration_is_grid(self):
        t = Track()
        t.add(Note("C", 4, 0.01))   # very short
        q = t.quantize(grid=0.25)
        assert q.beats[0].event.duration == 0.25  # at least one grid unit

    def test_preserves_total_beat_count_approx(self):
        t = Track()
        t.add(Note("C", 4, 1.0))
        t.add(Note("E", 4, 0.5))
        t.add(Note("G", 4, 0.5))
        q = t.quantize(grid=0.25)
        assert abs(q.total_beats - t.total_beats) < 0.5

    def test_does_not_mutate_original(self):
        t = Track()
        t.add(Note("C", 4, 0.33))
        _ = t.quantize(grid=0.25)
        assert t.beats[0].event.duration == 0.33  # original unchanged

    def test_chord_quantized(self):
        t = Track()
        t.add(Chord("C", "maj", 4, duration=0.37))
        q = t.quantize(grid=0.25)
        assert q.beats[0].event.duration == 0.25 or q.beats[0].event.duration == 0.5


class TestExportStems:
    def test_creates_files(self):
        import tempfile
        song = Song(title="Stem Test", bpm=120, sample_rate=22050)
        song.add_track(Track(name="kick", instrument="drums_kick")).add(Note("C", 2, 2.0))
        song.add_track(Track(name="bass", instrument="bass")).add(Note("E", 2, 2.0))
        with tempfile.TemporaryDirectory() as tmp:
            paths = song.export_stems(tmp)
            assert len(paths) == 2
            assert all(p.exists() for p in paths)
            assert any("kick" in p.name for p in paths)
            assert any("bass" in p.name for p in paths)

    def test_stem_files_have_audio(self):
        import tempfile
        import wave
        song = Song(title="Stem Test", bpm=120, sample_rate=22050)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 4, 1.0))
        with tempfile.TemporaryDirectory() as tmp:
            paths = song.export_stems(tmp)
            with wave.open(str(paths[0]), "rb") as wf:
                assert wf.getnframes() > 0
