"""Tests for music theory intelligence: chord-scale, tensions, generators, diffing."""

from __future__ import annotations

import pytest

from code_music import Note, Song, Track
from code_music.theory import (
    Change,
    available_tensions,
    chord_scale,
    generate_bass_line,
    generate_chord_melody,
    generate_counterpoint,
    generate_drums,
    song_diff,
    song_patch,
)

SR = 22050


class TestChordScale:
    def test_min7_includes_dorian(self):
        scales = chord_scale("C", "min7")
        assert "dorian" in scales

    def test_min7_includes_aeolian(self):
        scales = chord_scale("C", "min7")
        assert "aeolian" in scales

    def test_dom7_includes_mixolydian(self):
        scales = chord_scale("G", "dom7")
        assert "mixolydian" in scales

    def test_maj7_includes_major(self):
        scales = chord_scale("C", "maj7")
        assert "major" in scales

    def test_different_roots(self):
        s1 = chord_scale("C", "min7")
        s2 = chord_scale("A", "min7")
        assert s1 == s2  # same quality = same compatible scale types

    def test_unknown_shape_raises(self):
        with pytest.raises(ValueError, match="Unknown chord shape"):
            chord_scale("C", "imaginary")

    def test_returns_sorted(self):
        scales = chord_scale("C", "dom7")
        assert scales == sorted(scales)


class TestAvailableTensions:
    def test_min7_has_tensions(self):
        tensions = available_tensions("C", "min7")
        assert len(tensions) > 0

    def test_dom7_has_tensions(self):
        tensions = available_tensions("G", "dom7")
        assert len(tensions) > 0

    def test_unknown_shape_raises(self):
        with pytest.raises(ValueError, match="Unknown chord shape"):
            available_tensions("C", "imaginary")

    def test_returns_string_list(self):
        tensions = available_tensions("C", "maj7")
        assert all(isinstance(t, str) for t in tensions)


class TestGenerateBassLine:
    def test_root_style(self):
        chords = [("C", "min7"), ("F", "dom7")]
        notes = generate_bass_line(chords, style="root")
        assert len(notes) > 0
        assert all(isinstance(n, Note) for n in notes)

    def test_root_fifth_style(self):
        notes = generate_bass_line([("C", "min7")], style="root_fifth")
        assert len(notes) > 0

    def test_walking_style(self):
        notes = generate_bass_line([("C", "min7"), ("G", "dom7")], style="walking", seed=42)
        assert len(notes) > 0

    def test_syncopated_style(self):
        notes = generate_bass_line([("A", "min7")], style="syncopated")
        assert len(notes) > 0
        # Should have rests
        rests = [n for n in notes if n.pitch is None]
        assert len(rests) > 0

    def test_unknown_style_raises(self):
        with pytest.raises(ValueError, match="Unknown bass style"):
            generate_bass_line([("C", "min7")], style="funk")

    def test_bars_per_chord(self):
        notes = generate_bass_line([("C", "min7")], style="root", bars_per_chord=2)
        notes_1bar = generate_bass_line([("C", "min7")], style="root", bars_per_chord=1)
        assert len(notes) == 2 * len(notes_1bar)

    def test_in_track(self):
        song = Song(title="Bass Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
        notes = generate_bass_line([("C", "min7"), ("G", "dom7")], style="root")
        tr.extend(notes)
        audio = song.render()
        assert audio.shape[0] > 0


class TestGenerateDrums:
    def test_rock(self):
        d = generate_drums("rock", bars=2)
        assert "kick" in d and "snare" in d and "hat" in d
        assert len(d["kick"]) > 0

    def test_jazz(self):
        d = generate_drums("jazz", bars=2)
        assert len(d["kick"]) > 0

    def test_electronic(self):
        d = generate_drums("electronic", bars=2)
        assert len(d["kick"]) > 0

    def test_latin(self):
        d = generate_drums("latin", bars=2)
        assert len(d["kick"]) > 0

    def test_hiphop(self):
        d = generate_drums("hiphop", bars=2)
        assert len(d["kick"]) > 0

    def test_unknown_genre_raises(self):
        with pytest.raises(ValueError, match="Unknown drum genre"):
            generate_drums("polka")

    def test_in_song(self):
        song = Song(title="Drums Test", bpm=120, sample_rate=SR)
        drums = generate_drums("rock", bars=2)
        for name, notes in drums.items():
            instr = {"kick": "drums_kick", "snare": "drums_snare", "hat": "drums_hat"}[name]
            tr = song.add_track(Track(name=name, instrument=instr, volume=0.5))
            tr.extend(notes)
        audio = song.render()
        assert audio.shape[0] > 0


class TestGenerateChordMelody:
    def test_basic(self):
        chords = [("C", "maj"), ("G", "dom7")]
        notes = generate_chord_melody(chords, seed=42)
        assert len(notes) == 8  # 4 per chord default
        assert all(isinstance(n, Note) for n in notes)

    def test_arch_contour(self):
        notes = generate_chord_melody([("C", "maj7"), ("F", "maj7")], contour="arch", seed=42)
        assert len(notes) > 0

    def test_descending_contour(self):
        notes = generate_chord_melody([("A", "min7")], contour="descending", seed=42)
        assert len(notes) == 4

    def test_wave_contour(self):
        notes = generate_chord_melody([("C", "maj"), ("G", "dom7")], contour="wave", seed=42)
        assert len(notes) == 8

    def test_random_contour(self):
        notes = generate_chord_melody([("C", "maj")], contour="random", seed=42)
        assert len(notes) == 4

    def test_reproducible(self):
        a = generate_chord_melody([("C", "maj")], seed=42)
        b = generate_chord_melody([("C", "maj")], seed=42)
        assert [n.pitch for n in a] == [n.pitch for n in b]

    def test_in_song(self):
        melody = generate_chord_melody([("C", "min7"), ("G", "dom7")], seed=42)
        song = Song(title="Melody Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano", volume=0.5))
        tr.extend(melody)
        audio = song.render()
        assert audio.shape[0] > 0


class TestGenerateCounterpoint:
    def test_basic(self):
        melody = [Note("C", 4, 1.0), Note("D", 4, 1.0), Note("E", 4, 1.0)]
        cp = generate_counterpoint(melody, seed=42)
        assert len(cp) == 3
        assert all(isinstance(n, Note) for n in cp)

    def test_rests_preserved(self):
        melody = [Note("C", 4, 1.0), Note.rest(1.0), Note("E", 4, 1.0)]
        cp = generate_counterpoint(melody, seed=42)
        assert cp[1].pitch is None

    def test_third_interval(self):
        melody = [Note("C", 4, 1.0)]
        cp = generate_counterpoint(melody, interval="third", seed=42)
        assert cp[0].pitch is not None

    def test_sixth_interval(self):
        melody = [Note("C", 4, 1.0)]
        cp = generate_counterpoint(melody, interval="sixth", seed=42)
        assert cp[0].pitch is not None

    def test_velocity_reduced(self):
        melody = [Note("C", 4, 1.0, velocity=1.0)]
        cp = generate_counterpoint(melody, seed=42)
        assert cp[0].velocity < 1.0

    def test_in_song(self):
        melody = [Note(n, 4, 1.0) for n in ["C", "D", "E", "F", "G", "A", "B", "C"]]
        cp = generate_counterpoint(melody, seed=42)
        song = Song(title="CP Test", bpm=120, sample_rate=SR)
        song.add_track(Track(name="melody", instrument="piano", volume=0.5)).extend(melody)
        song.add_track(Track(name="cp", instrument="piano", volume=0.4)).extend(cp)
        audio = song.render()
        assert audio.shape[0] > 0


class TestSongDiff:
    def test_identical_songs(self):
        a = Song(title="Same", bpm=120, sample_rate=SR)
        a.add_track(Track(name="lead", instrument="piano"))
        b = Song(title="Same", bpm=120, sample_rate=SR)
        b.add_track(Track(name="lead", instrument="piano"))
        changes = song_diff(a, b)
        assert len(changes) == 0

    def test_track_added(self):
        a = Song(title="A", bpm=120, sample_rate=SR)
        b = Song(title="A", bpm=120, sample_rate=SR)
        b.add_track(Track(name="bass", instrument="bass"))
        changes = song_diff(a, b)
        assert any(c.change_type == "added" and c.track_name == "bass" for c in changes)

    def test_track_removed(self):
        a = Song(title="A", bpm=120, sample_rate=SR)
        a.add_track(Track(name="bass", instrument="bass"))
        b = Song(title="A", bpm=120, sample_rate=SR)
        changes = song_diff(a, b)
        assert any(c.change_type == "removed" and c.track_name == "bass" for c in changes)

    def test_bpm_changed(self):
        a = Song(title="A", bpm=120, sample_rate=SR)
        b = Song(title="A", bpm=140, sample_rate=SR)
        changes = song_diff(a, b)
        assert any(c.track_name == "_song" and "bpm" in c.detail for c in changes)

    def test_volume_changed(self):
        a = Song(title="A", bpm=120, sample_rate=SR)
        a.add_track(Track(name="lead", instrument="piano", volume=0.5))
        b = Song(title="A", bpm=120, sample_rate=SR)
        b.add_track(Track(name="lead", instrument="piano", volume=0.8))
        changes = song_diff(a, b)
        assert any(c.track_name == "lead" and "volume" in c.detail for c in changes)

    def test_change_repr(self):
        c = Change("added", "bass", "instrument=bass, 8 beats")
        r = repr(c)
        assert "Change" in r
        assert "added" in r


class TestSongPatch:
    def test_patch_add_track(self):
        base = Song(title="Base", bpm=120, sample_rate=SR)
        changes = [Change("added", "bass", "instrument=bass, 0 beats")]
        song_patch(base, changes)
        assert any(t.name == "bass" for t in base.tracks)

    def test_patch_remove_track(self):
        base = Song(title="Base", bpm=120, sample_rate=SR)
        base.add_track(Track(name="bass", instrument="bass"))
        changes = [Change("removed", "bass", "")]
        song_patch(base, changes)
        assert not any(t.name == "bass" for t in base.tracks)

    def test_patch_modify_volume(self):
        base = Song(title="Base", bpm=120, sample_rate=SR)
        base.add_track(Track(name="lead", instrument="piano", volume=0.5))
        changes = [Change("modified", "lead", "volume: 0.5 → 0.8")]
        song_patch(base, changes)
        assert base.tracks[0].volume == 0.8

    def test_patch_modify_bpm(self):
        base = Song(title="Base", bpm=120, sample_rate=SR)
        changes = [Change("modified", "_song", "bpm: 120 → 140")]
        song_patch(base, changes)
        assert base.bpm == 140.0
