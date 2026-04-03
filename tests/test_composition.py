"""Tests for composition tools: melody continuation, sections, lead sheets."""

from __future__ import annotations

import numpy as np

from code_music import Chord, Note, Song, Track
from code_music.composition import (
    Bridge,
    Chorus,
    Intro,
    Outro,
    Verse,
    continue_melody,
    song_map,
    to_lead_sheet,
    to_tab,
)
from code_music.theory import analyze_harmony

SR = 22050


class TestContinueMelody:
    def test_basic_continuation(self):
        seed = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0)]
        result = continue_melody(seed, bars=2, key="C", mode="major", seed_rng=42)
        assert len(result) > len(seed)

    def test_returns_notes(self):
        seed = [Note("A", 4, 0.5), Note("C", 5, 0.5)]
        result = continue_melody(seed, bars=1, seed_rng=42)
        assert all(isinstance(n, Note) for n in result)

    def test_includes_seed(self):
        seed = [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        result = continue_melody(seed, bars=1, seed_rng=42)
        # First notes should be the seed
        assert result[0].pitch == "C"
        assert result[1].pitch == "E"

    def test_reproducible(self):
        seed = [Note("C", 5, 0.5), Note("D", 5, 0.5), Note("E", 5, 0.5)]
        a = continue_melody(seed, bars=2, seed_rng=42)
        b = continue_melody(seed, bars=2, seed_rng=42)
        assert [n.pitch for n in a] == [n.pitch for n in b]

    def test_different_seeds_differ(self):
        seed = [Note("C", 5, 0.5), Note("D", 5, 0.5), Note("E", 5, 0.5)]
        a = continue_melody(seed, bars=2, seed_rng=42)
        b = continue_melody(seed, bars=2, seed_rng=99)
        assert [n.pitch for n in a] != [n.pitch for n in b]

    def test_minor_key(self):
        seed = [Note("A", 4, 0.5), Note("C", 5, 0.5)]
        result = continue_melody(seed, bars=1, key="A", mode="minor", seed_rng=42)
        assert len(result) > 2

    def test_pentatonic(self):
        seed = [Note("C", 5, 0.5)]
        result = continue_melody(seed, bars=1, key="C", mode="pentatonic", seed_rng=42)
        assert len(result) > 1

    def test_empty_seed(self):
        result = continue_melody([], bars=1, key="C", seed_rng=42)
        assert len(result) > 0

    def test_in_song(self):
        seed = [Note("C", 5, 0.5), Note("E", 5, 0.5), Note("G", 5, 0.5)]
        melody = continue_melody(seed, bars=2, seed_rng=42)
        song = Song(title="Melody Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano", volume=0.5))
        tr.extend(melody)
        audio = song.render()
        assert np.max(np.abs(audio)) > 0.0

    def test_order_2(self):
        seed = [Note("C", 5, 0.5), Note("D", 5, 0.5), Note("E", 5, 0.5), Note("F", 5, 0.5)]
        result = continue_melody(seed, bars=2, order=2, seed_rng=42)
        assert len(result) > len(seed)


class TestNamedSections:
    def test_verse(self):
        v = Verse(bars=8)
        assert v.name == "verse"
        assert v.bars == 8

    def test_chorus(self):
        c = Chorus(bars=8)
        assert c.name == "chorus"

    def test_bridge(self):
        b = Bridge(bars=4)
        assert b.name == "bridge"

    def test_intro(self):
        i = Intro(bars=4)
        assert i.name == "intro"

    def test_outro(self):
        o = Outro(bars=4)
        assert o.name == "outro"

    def test_verse_add_track(self):
        v = Verse(bars=4)
        v.add_track("lead", [Note("C", 5, 1.0)])
        assert "lead" in v.tracks

    def test_chorus_repeat(self):
        c = Chorus(bars=4)
        reps = c.repeat(3)
        assert len(reps) == 3
        assert all(r.name == "chorus" for r in reps)

    def test_repr(self):
        v = Verse(bars=8)
        assert "verse" in repr(v)


class TestLeadSheet:
    def test_basic(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="pad", instrument="pad"))
        tr.add(Chord("C", "min7", 3, duration=4.0))
        tr.add(Chord("G", "dom7", 3, duration=4.0))
        lead = song.add_track(Track(name="lead", instrument="piano"))
        for n in ["C", "Eb", "G", "Bb"]:
            lead.add(Note(n, 5, 1.0))
        for n in ["G", "B", "D", "F"]:
            lead.add(Note(n, 5, 1.0))

        result = to_lead_sheet(song)
        assert "Lead Sheet" in result
        assert "Cmin7" in result
        assert "Gdom7" in result

    def test_empty_song(self):
        song = Song(title="Empty", bpm=120, sample_rate=SR)
        result = to_lead_sheet(song)
        assert "empty song" in result

    def test_title_and_bpm(self):
        song = Song(title="My Song", bpm=140, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 4.0))
        result = to_lead_sheet(song)
        assert "My Song" in result
        assert "140" in result

    def test_melody_notes_appear(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("E", 5, 1.0))
        tr.add(Note("G", 5, 1.0))
        result = to_lead_sheet(song)
        assert "E" in result
        assert "G" in result

    def test_returns_string(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 4.0))
        assert isinstance(to_lead_sheet(song), str)


class TestToTab:
    def test_basic_guitar(self):
        song = Song(title="Tab Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("E", 4, 1.0))
        tr.add(Note("A", 4, 1.0))
        result = to_tab(song, tuning="guitar")
        assert "TAB" in result
        assert "Guitar" in result

    def test_bass_tuning(self):
        song = Song(title="Tab Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="bass", instrument="bass"))
        tr.add(Note("E", 2, 1.0))
        result = to_tab(song, tuning="bass")
        assert "Bass" in result

    def test_empty_song(self):
        song = Song(title="Empty", bpm=120, sample_rate=SR)
        result = to_tab(song)
        assert "no melodic track" in result

    def test_specific_track(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        song.add_track(Track(name="kick", instrument="drums_kick")).add(Note("C", 2, 1.0))
        song.add_track(Track(name="lead", instrument="piano")).add(Note("E", 4, 1.0))
        result = to_tab(song, track_name="lead")
        assert "TAB" in result

    def test_returns_string(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 1.0))
        assert isinstance(to_tab(song), str)


class TestSongMap:
    def test_basic(self):
        song = Song(title="Map Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        for _ in range(8):
            tr.add(Note("C", 5, 1.0))
        result = song_map(song)
        assert "Song Map" in result
        assert "lead" in result

    def test_multiple_tracks(self):
        song = Song(title="Multi", bpm=120, sample_rate=SR)
        song.add_track(Track(name="kick", instrument="drums_kick")).add(Note("C", 2, 4.0))
        song.add_track(Track(name="pad", instrument="pad")).add(Chord("C", "min7", 3, duration=4.0))
        result = song_map(song)
        assert "kick" in result
        assert "pad" in result

    def test_empty_song(self):
        song = Song(title="Empty", bpm=120, sample_rate=SR)
        result = song_map(song)
        assert "Song Map" in result

    def test_returns_string(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 4.0))
        assert isinstance(song_map(song), str)


class TestAnalyzeHarmony:
    def test_basic_progression(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="pad", instrument="pad"))
        tr.add(Chord("C", "maj7", 3, duration=4.0))
        tr.add(Chord("G", "dom7", 3, duration=4.0))
        result = analyze_harmony(song, key="C")
        assert len(result) == 2
        assert result[0]["roman"] == "I"
        assert result[1]["roman"] == "V"

    def test_minor_chords(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="pad", instrument="pad"))
        tr.add(Chord("D", "min7", 3, duration=4.0))
        result = analyze_harmony(song, key="C")
        assert result[0]["roman"] == "ii"  # lowercase for minor

    def test_function_labels(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="pad", instrument="pad"))
        tr.add(Chord("C", "maj7", 3, duration=4.0))
        tr.add(Chord("F", "maj7", 3, duration=4.0))
        tr.add(Chord("G", "dom7", 3, duration=4.0))
        result = analyze_harmony(song, key="C")
        assert result[0]["function"] == "tonic"
        assert result[1]["function"] == "subdominant"
        assert result[2]["function"] == "dominant"

    def test_uses_key_sig(self):
        song = Song(title="Test", bpm=120, sample_rate=SR, key_sig="G")
        tr = song.add_track(Track(name="pad", instrument="pad"))
        tr.add(Chord("G", "maj7", 3, duration=4.0))
        result = analyze_harmony(song)
        assert result[0]["roman"] == "I"

    def test_returns_list(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="pad", instrument="pad"))
        tr.add(Chord("C", "min7", 3, duration=4.0))
        result = analyze_harmony(song, key="C")
        assert isinstance(result, list)
        assert "beat" in result[0]
        assert "roman" in result[0]

    def test_empty_song(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        result = analyze_harmony(song, key="C")
        assert result == []
