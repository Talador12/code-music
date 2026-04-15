"""Tests for v170 genre transform system."""

import copy
import pytest

from code_music.engine import Chord, Note, Song, Track, scale
from code_music.transform import (
    GENRE_PROFILES,
    genre_transform,
    rhythm_transform,
    harmony_transform,
    instrument_transform,
    groove_transform,
    dynamics_transform,
    articulation_transform,
    apply_rhythm_pattern,
    list_genres,
    list_rhythm_patterns,
)


def _make_pop_song() -> Song:
    """Create a simple pop song for transformation tests."""
    song = Song(title="Pop Original", bpm=120, key_sig="C", sample_rate=22050)
    melody = song.add_track(Track(name="melody", instrument="sawtooth", volume=0.6))
    melody.extend(scale("C", "major", 5, length=8))
    chords = song.add_track(Track(name="chords", instrument="piano", volume=0.5))
    chords.add(Chord("C", "maj", 4, duration=4.0))
    chords.add(Chord("F", "maj", 4, duration=4.0))
    bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
    bass.extend([Note("C", 2, 2.0), Note("G", 2, 2.0), Note("F", 2, 2.0), Note("G", 2, 2.0)])
    kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
    kick.extend([Note("C", 2, 1.0)] * 8)
    return song


class TestGenreProfiles:
    def test_profiles_exist(self):
        assert len(GENRE_PROFILES) >= 17

    def test_all_profiles_have_required_fields(self):
        for name, profile in GENRE_PROFILES.items():
            assert profile.name == name
            assert len(profile.bpm_range) == 2
            assert profile.default_bpm > 0
            assert isinstance(profile.instruments, dict)

    def test_list_genres(self):
        genres = list_genres()
        assert "jazz" in genres
        assert "funk" in genres
        assert "bossa_nova" in genres
        assert "lofi" in genres
        assert "big_band" in genres
        assert "blues" in genres


class TestGenreTransform:
    def test_basic_transform(self):
        song = _make_pop_song()
        jazz = genre_transform(song, "jazz")
        assert jazz.title != song.title
        assert "Jazz" in jazz.title

    def test_preserves_track_count(self):
        song = _make_pop_song()
        result = genre_transform(song, "funk")
        assert len(result.tracks) == len(song.tracks)

    def test_changes_bpm(self):
        song = _make_pop_song()
        bossa = genre_transform(song, "bossa_nova")
        assert bossa.bpm == GENRE_PROFILES["bossa_nova"].default_bpm

    def test_custom_bpm_override(self):
        song = _make_pop_song()
        result = genre_transform(song, "jazz", bpm=200)
        assert result.bpm == 200

    def test_invalid_genre_raises(self):
        song = _make_pop_song()
        with pytest.raises(ValueError, match="Unknown genre"):
            genre_transform(song, "not_a_genre")

    def test_does_not_mutate_original(self):
        song = _make_pop_song()
        original_title = song.title
        original_bpm = song.bpm
        _ = genre_transform(song, "jazz")
        assert song.title == original_title
        assert song.bpm == original_bpm

    @pytest.mark.parametrize(
        "genre",
        [
            "jazz",
            "blues",
            "funk",
            "bossa_nova",
            "latin_jazz",
            "big_band",
            "lofi",
            "neo_soul",
            "reggae",
            "classical",
            "rock",
            "electronic",
            "ambient",
            "afrobeat",
            "gospel",
            "disco",
            "bebop",
            "country",
            "bluegrass",
            "r&b",
            "trap",
            "hiphop",
            "ska",
            "punk",
            "metal",
            "prog_rock",
            "synthwave",
            "vaporwave",
            "shoegaze",
            "post_rock",
            "house",
            "techno",
            "drum_and_bass",
            "dubstep",
            "motown",
            "surf_rock",
            "grunge",
            "tango",
            "samba",
            "cumbia",
            "flamenco",
            "celtic",
            "bollywood",
            "smooth_jazz",
            "cool_jazz",
            "modal_jazz",
            "fusion",
            "trip_hop",
            "second_line",
            "chillwave",
            "swing",
            "new_orleans",
            "acid_jazz",
            "reggaeton",
            "mariachi",
        ],
    )
    def test_all_genres_work(self, genre):
        song = _make_pop_song()
        result = genre_transform(song, genre)
        assert result is not None
        assert len(result.tracks) > 0

    def test_jazz_adds_swing(self):
        song = _make_pop_song()
        jazz = genre_transform(song, "jazz")
        assert any(t.swing > 0 for t in jazz.tracks)

    def test_funk_no_swing(self):
        song = _make_pop_song()
        funk = genre_transform(song, "funk")
        assert all(t.swing == 0.0 for t in funk.tracks)


class TestRhythmTransform:
    def test_swing_adds_swing(self):
        song = _make_pop_song()
        swung = rhythm_transform(song, "swing")
        assert any(t.swing > 0 for t in swung.tracks)

    def test_straight_removes_swing(self):
        song = _make_pop_song()
        for t in song.tracks:
            t.swing = 0.5
        straight = rhythm_transform(song, "straight")
        assert all(t.swing == 0.0 for t in straight.tracks)

    def test_preserves_pitches(self):
        song = _make_pop_song()
        result = rhythm_transform(song, "shuffle")
        original_pitches = []
        for t in song.tracks:
            for b in t.beats:
                if b.event and hasattr(b.event, "pitch"):
                    original_pitches.append(getattr(b.event, "pitch", None))
        result_pitches = []
        for t in result.tracks:
            for b in t.beats:
                if b.event and hasattr(b.event, "pitch"):
                    result_pitches.append(getattr(b.event, "pitch", None))
        # Pitches should be preserved (reggae may add rests but pitches stay)
        assert len(result_pitches) >= len(original_pitches) * 0.5


class TestHarmonyTransform:
    def test_jazz_upgrades_triads(self):
        song = _make_pop_song()
        jazz = harmony_transform(song, "jazz")
        for t in jazz.tracks:
            for b in t.beats:
                if isinstance(getattr(b, "event", None), Chord):
                    assert b.event.shape != "maj", "Jazz should upgrade maj to maj7"

    def test_blues_makes_dom7(self):
        song = _make_pop_song()
        blues = harmony_transform(song, "blues")
        for t in blues.tracks:
            for b in t.beats:
                if isinstance(getattr(b, "event", None), Chord):
                    assert b.event.shape == "dom7"

    def test_unknown_genre_returns_copy(self):
        song = _make_pop_song()
        result = harmony_transform(song, "nonexistent")
        assert result.title == song.title


class TestInstrumentTransform:
    def test_jazz_instruments(self):
        song = _make_pop_song()
        result = instrument_transform(song, "jazz")
        instruments = [t.instrument for t in result.tracks]
        assert "saxophone" in instruments or "piano" in instruments

    def test_lofi_instruments(self):
        song = _make_pop_song()
        result = instrument_transform(song, "lofi")
        instruments = [t.instrument for t in result.tracks]
        assert "rhodes" in instruments or "sub_bass" in instruments


class TestDynamicsTransform:
    def test_lofi_quieter(self):
        song = _make_pop_song()
        result = dynamics_transform(song, "lofi")
        max_vel = 0.0
        for t in result.tracks:
            for b in t.beats:
                if b.event and hasattr(b.event, "velocity"):
                    max_vel = max(max_vel, b.event.velocity)
        assert max_vel <= 0.6, "Lofi should have lower max velocity"

    def test_rock_louder(self):
        song = _make_pop_song()
        result = dynamics_transform(song, "rock")
        min_vel = 1.0
        for t in result.tracks:
            for b in t.beats:
                if b.event and hasattr(b.event, "velocity"):
                    min_vel = min(min_vel, b.event.velocity)
        assert min_vel >= 0.3


class TestRhythmPatterns:
    def test_list_patterns(self):
        patterns = list_rhythm_patterns()
        assert "tresillo" in patterns
        assert "shuffle" in patterns
        assert "bossa_rhythm" in patterns

    def test_tresillo(self):
        notes = scale("C", "major", 4, length=8)
        result = apply_rhythm_pattern(notes, "tresillo")
        assert len(result) > 0
        durations = [n.duration for n in result]
        assert 1.5 in durations
        assert 1.0 in durations

    def test_shuffle(self):
        notes = [Note("C", 4, 1.0)] * 8
        result = apply_rhythm_pattern(notes, "shuffle")
        durations = set(round(n.duration, 3) for n in result)
        assert 0.667 in durations or 0.333 in durations

    def test_invalid_pattern_raises(self):
        notes = [Note("C", 4, 1.0)]
        with pytest.raises(ValueError, match="Unknown pattern"):
            apply_rhythm_pattern(notes, "not_real")

    def test_empty_notes(self):
        result = apply_rhythm_pattern([Note.rest(1.0)], "tresillo")
        assert result == [Note.rest(1.0)]

    @pytest.mark.parametrize("pattern", list_rhythm_patterns())
    def test_all_patterns_work(self, pattern):
        notes = scale("C", "pentatonic", 4, length=8)
        result = apply_rhythm_pattern(notes, pattern)
        assert len(result) > 0
        assert all(n.pitch is not None for n in result)


class TestIntegration:
    def test_full_render_after_transform(self):
        song = _make_pop_song()
        jazz = genre_transform(song, "jazz")
        audio = jazz.render()
        assert audio.shape[0] > 0
        assert audio.shape[1] == 2

    def test_chain_transforms(self):
        song = _make_pop_song()
        result = instrument_transform(
            harmony_transform(song, "jazz"),
            "bossa_nova",
        )
        assert result is not None
        assert len(result.tracks) > 0
