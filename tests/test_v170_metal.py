"""Tests for v170 metal engine: dual guitar harmony, drop tuning, metal drums, riffs."""

import pytest

from code_music.engine import Note, Chord, Song, Track, scale
from code_music.theory.rhythm import (
    harmonize_lead,
    dual_guitar,
    drop_tuning,
    metal_drum_pattern,
    palm_mute_chug,
    clean_arpeggio,
)
from code_music.transform import genre_transform, GENRE_PROFILES


class TestMetalGenreProfiles:
    def test_melodic_metalcore_exists(self):
        assert "melodic_metalcore" in GENRE_PROFILES

    def test_nwoahm_exists(self):
        assert "nwoahm" in GENRE_PROFILES

    def test_prog_metal_exists(self):
        assert "prog_metal" in GENRE_PROFILES

    def test_post_hardcore_exists(self):
        assert "post_hardcore" in GENRE_PROFILES

    def test_djent_exists(self):
        assert "djent" in GENRE_PROFILES

    def test_melodic_metalcore_has_dual_panning(self):
        p = GENRE_PROFILES["melodic_metalcore"]
        # Guitar L and pad (guitar R) should be panned apart
        assert p.pans.get("melody", 0) < 0  # left
        assert p.pans.get("pad", 0) > 0  # right

    @pytest.mark.parametrize(
        "genre",
        [
            "melodic_metalcore",
            "nwoahm",
            "prog_metal",
            "post_hardcore",
            "djent",
        ],
    )
    def test_all_metal_variants_transform(self, genre):
        song = Song(title="Test", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(name="melody", instrument="sawtooth"))
        tr.extend(scale("E", "minor", 5, length=8))
        ch = song.add_track(Track(name="chords", instrument="sawtooth"))
        ch.add(Chord("E", "power5", 3, duration=8.0))
        result = genre_transform(song, genre)
        assert result is not None


class TestHarmonizeLead:
    def test_basic_harmony_in_thirds(self):
        melody = scale("E", "minor", 5, length=8)
        harmony = harmonize_lead(melody, interval=-3, key="E", scale_name="minor")
        assert len(harmony) == len(melody)
        # Harmony should be lower
        for m, h in zip(melody, harmony):
            if m.midi is not None and h.midi is not None:
                assert h.midi < m.midi

    def test_harmony_preserves_rhythm(self):
        melody = [Note("E", 5, 0.5), Note("G", 5, 1.0), Note("B", 5, 0.25)]
        harmony = harmonize_lead(melody, interval=-3, key="E", scale_name="minor")
        for m, h in zip(melody, harmony):
            assert m.duration == h.duration

    def test_harmony_preserves_rests(self):
        melody = [Note("E", 5, 1.0), Note.rest(1.0), Note("G", 5, 1.0)]
        harmony = harmonize_lead(melody, interval=-3, key="E", scale_name="minor")
        assert harmony[1].pitch is None

    def test_harmony_preserves_velocity(self):
        melody = [Note("E", 5, 1.0, velocity=0.9)]
        harmony = harmonize_lead(melody, interval=-3, key="E", scale_name="minor")
        assert harmony[0].velocity == 0.9

    def test_harmony_preserves_articulation(self):
        melody = [Note("E", 5, 1.0, articulation="legato")]
        harmony = harmonize_lead(melody, interval=-3, key="E", scale_name="minor")
        assert harmony[0].articulation == "legato"

    def test_octave_harmony(self):
        melody = [Note("E", 5, 1.0)]
        harmony = harmonize_lead(melody, interval=-8, key="E", scale_name="minor")
        # Octave below should be roughly 12 semitones lower
        assert abs(harmony[0].midi - melody[0].midi) >= 10

    def test_harmony_above(self):
        melody = [Note("E", 4, 1.0)]
        harmony = harmonize_lead(melody, interval=3, key="E", scale_name="minor")
        assert harmony[0].midi > melody[0].midi

    def test_major_key_harmony(self):
        melody = scale("C", "major", 5, length=4)
        harmony = harmonize_lead(melody, interval=-3, key="C", scale_name="major")
        assert len(harmony) == 4
        assert all(h.midi is not None for h in harmony)


class TestDualGuitar:
    def test_returns_four_values(self):
        melody = scale("E", "minor", 5, length=4)
        result = dual_guitar(melody, key="E", scale_name="minor")
        assert len(result) == 4
        left, right, pan_l, pan_r = result
        assert len(left) == len(right) == 4

    def test_panning_is_opposite(self):
        melody = [Note("E", 5, 1.0)]
        _, _, pan_l, pan_r = dual_guitar(melody, key="E")
        assert pan_l < 0
        assert pan_r > 0
        assert abs(pan_l) == abs(pan_r)

    def test_custom_pan_width(self):
        melody = [Note("E", 5, 1.0)]
        _, _, pan_l, pan_r = dual_guitar(melody, key="E", pan_width=1.0)
        assert pan_l == -1.0
        assert pan_r == 1.0


class TestDropTuning:
    def test_drop_d(self):
        notes = [Note("E", 2, 1.0)]
        dropped = drop_tuning(notes, "drop_d")
        assert dropped[0].midi == notes[0].midi - 2

    def test_drop_c(self):
        notes = [Note("E", 2, 1.0)]
        dropped = drop_tuning(notes, "drop_c")
        assert dropped[0].midi == notes[0].midi - 4

    def test_drop_b(self):
        notes = [Note("E", 2, 1.0)]
        dropped = drop_tuning(notes, "drop_b")
        assert dropped[0].midi == notes[0].midi - 5

    def test_standard_no_change(self):
        notes = [Note("E", 2, 1.0)]
        result = drop_tuning(notes, "standard")
        assert result[0].midi == notes[0].midi

    def test_preserves_rests(self):
        notes = [Note.rest(1.0)]
        dropped = drop_tuning(notes, "drop_c")
        assert dropped[0].pitch is None


class TestMetalDrumPattern:
    def test_double_bass(self):
        drums = metal_drum_pattern(bars=1, style="double_bass", seed=42)
        kick = drums["kick"]
        assert len(kick) == 16
        # Every step should have a kick hit (constant double bass)
        assert all(n.pitch is not None for n in kick)

    def test_blast_beat(self):
        drums = metal_drum_pattern(bars=1, style="blast_beat")
        kick = drums["kick"]
        snare = drums["snare"]
        # Kick and snare alternate
        kick_hits = sum(1 for n in kick if n.pitch is not None)
        snare_hits = sum(1 for n in snare if n.pitch is not None)
        assert kick_hits == 8
        assert snare_hits == 8

    def test_half_time(self):
        drums = metal_drum_pattern(bars=1, style="half_time")
        kick = drums["kick"]
        kick_hits = sum(1 for n in kick if n.pitch is not None)
        # Half-time has fewer kick hits
        assert kick_hits < 8

    def test_gallop(self):
        drums = metal_drum_pattern(bars=1, style="gallop")
        kick = drums["kick"]
        kick_hits = sum(1 for n in kick if n.pitch is not None)
        # Gallop has triplet feel: ~12 hits per bar
        assert kick_hits >= 10

    def test_breakdown(self):
        drums = metal_drum_pattern(bars=1, style="breakdown")
        kick = drums["kick"]
        snare = drums["snare"]
        # Breakdown is sparse
        kick_hits = sum(1 for n in kick if n.pitch is not None)
        assert kick_hits <= 8


class TestPalmMuteChug:
    def test_straight_chug(self):
        result = palm_mute_chug("E", 2, bars=1, pattern="straight")
        assert len(result) == 16
        assert all(n.articulation == "muted" for n in result)
        assert all(n.pitch is not None for n in result)

    def test_syncopated_has_rests(self):
        result = palm_mute_chug("E", 2, bars=1, pattern="syncopated")
        assert len(result) == 16
        rests = sum(1 for n in result if n.pitch is None)
        assert rests > 0

    def test_syncopated_has_ghost_notes(self):
        result = palm_mute_chug("E", 2, bars=1, pattern="syncopated")
        ghost = [n for n in result if n.pitch is not None and n.velocity < 0.5]
        assert len(ghost) > 0

    def test_gallop_pattern(self):
        result = palm_mute_chug("E", 2, bars=1, pattern="gallop")
        assert len(result) == 16
        # Gallop has rests on every 4th position
        rests = sum(1 for n in result if n.pitch is None)
        assert rests == 4

    def test_djent_pattern(self):
        result = palm_mute_chug("E", 2, bars=1, pattern="djent")
        assert len(result) == 16
        # Djent is sparse stabs
        rests = sum(1 for n in result if n.pitch is None)
        assert rests > 6

    def test_breakdown_pattern(self):
        result = palm_mute_chug("E", 2, bars=1, pattern="breakdown")
        assert len(result) > 0
        # Breakdown notes are NOT muted (open strings ring)
        open_notes = [n for n in result if n.pitch is not None and n.articulation is None]
        assert len(open_notes) > 0


class TestCleanArpeggio:
    def test_ascending(self):
        result = clean_arpeggio("E", "min", 4, bars=1, style="ascending")
        assert len(result) == 4
        pitches = [n.midi for n in result]
        # Should be ascending
        assert pitches == sorted(pitches)

    def test_descending(self):
        result = clean_arpeggio("E", "min", 4, bars=1, style="descending")
        pitches = [n.midi for n in result]
        assert pitches == sorted(pitches, reverse=True)

    def test_fingerpick(self):
        result = clean_arpeggio("E", "min", 4, bars=1, style="fingerpick")
        assert len(result) == 8  # 8-note pattern

    def test_sweep(self):
        result = clean_arpeggio("E", "min", 4, bars=1, style="sweep")
        assert len(result) > 4  # up + down + hold

    def test_clean_velocity_is_soft(self):
        result = clean_arpeggio("C", "maj", 4, bars=1)
        assert all(n.velocity <= 0.6 for n in result)


class TestMetalIntegration:
    def test_full_metalcore_renders(self):
        song = Song(title="Metalcore Test", bpm=160, sample_rate=22050)

        # Dual harmony leads
        melody = scale("E", "minor", 5, length=8)
        left, right, pl, pr = dual_guitar(melody, key="E", scale_name="minor")
        gtr_l = song.add_track(Track(name="gtr_L", instrument="sawtooth", volume=0.65, pan=pl))
        gtr_l.extend(drop_tuning(left, "drop_c"))
        gtr_r = song.add_track(Track(name="gtr_R", instrument="sawtooth", volume=0.6, pan=pr))
        gtr_r.extend(drop_tuning(right, "drop_c"))

        # Rhythm chugs
        chug = palm_mute_chug("E", 2, bars=1, pattern="gallop")
        rhythm = song.add_track(Track(name="rhythm", instrument="sawtooth", volume=0.75))
        rhythm.extend(drop_tuning(chug, "drop_c"))

        # Clean section
        clean = clean_arpeggio("E", "min", 4, bars=1, style="fingerpick")
        cl = song.add_track(Track(name="clean", instrument="guitar_acoustic", volume=0.4))
        cl.extend(clean)

        # Drums
        drums = metal_drum_pattern(bars=2, style="double_bass", seed=42)
        kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.85))
        kick.extend(drums["kick"])
        snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.8))
        snare.extend(drums["snare"])

        audio = song.render()
        assert audio.shape[0] > 0
        assert audio.shape[1] == 2

    def test_genre_transform_to_melodic_metalcore(self):
        song = Song(title="Pop to Metal", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(name="melody", instrument="sawtooth"))
        tr.extend(scale("C", "major", 5, length=8))
        result = genre_transform(song, "melodic_metalcore")
        assert result.bpm == 160
        assert "Melodic Metalcore" in result.title
