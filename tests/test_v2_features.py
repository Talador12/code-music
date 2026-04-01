"""Tests for v2.0 features: Section.repeat, Track.concat, _effects deprecation."""

from __future__ import annotations

import warnings

from code_music.engine import Chord, Note, Section, Song, Track


class TestSectionRepeat:
    def test_repeat_returns_list_of_correct_length(self):
        s = Section("chorus", bars=4)
        s.add_track("lead", [Note("C", 4, 4.0)])
        copies = s.repeat(3)
        assert len(copies) == 3

    def test_repeat_returns_independent_copies(self):
        s = Section("verse", bars=4)
        s.add_track("pad", [Chord("A", "min", 3, duration=16.0)])
        copies = s.repeat(2)
        # Mutating one copy doesn't affect the other
        copies[0].add_track("bass", [Note("A", 2, 16.0)])
        assert "bass" not in copies[1].tracks

    def test_repeat_preserves_name_and_bars(self):
        s = Section("bridge", bars=2)
        copies = s.repeat(2)
        for c in copies:
            assert c.name == "bridge"
            assert c.bars == 2

    def test_repeat_zero_returns_empty_list(self):
        s = Section("x", bars=1)
        assert s.repeat(0) == []

    def test_repeat_works_in_arrange(self):
        intro = Section("intro", bars=2)
        intro.add_track("pad", [Chord("C", "maj", 3, duration=8.0)])

        chorus = Section("chorus", bars=2)
        chorus.add_track("pad", [Chord("G", "maj", 3, duration=8.0)])

        song = Song(bpm=120)
        song.arrange(
            [intro, *chorus.repeat(3)],
            instruments={"pad": "pad"},
        )

        # intro (8 beats) + 3 × chorus (8 beats) = 32 beats
        assert song.total_beats == 32.0


class TestTrackConcat:
    def test_concat_joins_beats(self):
        t1 = Track(instrument="piano")
        t1.add(Note("C", 4, 1.0))
        t1.add(Note("E", 4, 1.0))

        t2 = Track(instrument="piano")
        t2.add(Note("G", 4, 1.0))

        joined = t1.concat(t2)
        assert len(joined.beats) == 3

    def test_concat_preserves_metadata_from_self(self):
        t1 = Track(name="lead", instrument="sawtooth", volume=0.7, pan=0.2)
        t1.add(Note("C", 4, 1.0))

        t2 = Track(name="other", instrument="sine", volume=0.3, pan=-0.5)
        t2.add(Note("G", 4, 1.0))

        joined = t1.concat(t2)
        assert joined.name == "lead"
        assert joined.instrument == "sawtooth"
        assert joined.volume == 0.7
        assert joined.pan == 0.2

    def test_concat_total_beats_is_sum(self):
        t1 = Track()
        t1.add(Note("C", 4, 2.0))
        t1.add(Note("E", 4, 2.0))

        t2 = Track()
        t2.add(Note("G", 4, 3.0))

        joined = t1.concat(t2)
        assert joined.total_beats == 7.0

    def test_concat_does_not_mutate_originals(self):
        t1 = Track()
        t1.add(Note("C", 4, 1.0))

        t2 = Track()
        t2.add(Note("G", 4, 1.0))

        _ = t1.concat(t2)
        assert len(t1.beats) == 1
        assert len(t2.beats) == 1

    def test_concat_chains_with_fade(self):
        t1 = Track(instrument="piano")
        for _ in range(4):
            t1.add(Note("C", 4, 1.0))

        t2 = Track(instrument="piano")
        for _ in range(4):
            t2.add(Note("G", 4, 1.0))

        joined = t1.fade_in(2.0).concat(t2.fade_out(2.0))
        assert joined.total_beats == 8.0
        # First note should be quiet (fade in)
        assert joined.beats[0].event.velocity < 0.01
        # Last note should be quieter than middle
        assert joined.beats[7].event.velocity < joined.beats[4].event.velocity


class TestEffectsDeprecation:
    def test_setting_underscore_effects_warns(self):
        song = Song(title="Dep Test", bpm=120)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            song._effects = {"lead": lambda s, sr: s}
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "_effects" in str(w[0].message)

    def test_setting_underscore_effects_redirects_to_effects(self):
        song = Song(title="Redirect Test", bpm=120)
        fx = {"lead": lambda s, sr: s}
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            song._effects = fx
        assert song.effects is fx

    def test_getting_underscore_effects_warns(self):
        song = Song(title="Get Test", bpm=120)
        song.effects = {"pad": lambda s, sr: s}
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = song._effects
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
        assert result is song.effects

    def test_new_effects_attribute_works_without_warning(self):
        song = Song(title="Clean Test", bpm=120)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            song.effects = {"lead": lambda s, sr: s}
            # Filter only DeprecationWarnings about _effects
            dep_warnings = [x for x in w if "_effects" in str(x.message)]
            assert len(dep_warnings) == 0
