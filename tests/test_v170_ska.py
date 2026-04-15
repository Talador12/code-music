"""Tests for v170 ska infrastructure: all three waves plus the skank engine."""

import pytest

from code_music.engine import Note, Chord, Song, Track, scale
from code_music.theory.rhythm import (
    ska_drum_pattern,
    skank_pattern,
    ska_bass_line,
    ska_horn_riff,
)
from code_music.transform import genre_transform, GENRE_PROFILES


class TestSkaGenreProfiles:
    """All ska variants should be registered as genre profiles."""

    def test_ska_base_exists(self):
        assert "ska" in GENRE_PROFILES

    def test_first_wave_exists(self):
        assert "ska_first_wave" in GENRE_PROFILES

    def test_2tone_exists(self):
        assert "ska_2tone" in GENRE_PROFILES

    def test_third_wave_exists(self):
        assert "ska_third_wave" in GENRE_PROFILES

    def test_ska_punk_exists(self):
        assert "ska_punk" in GENRE_PROFILES

    def test_ska_jazz_exists(self):
        assert "ska_jazz" in GENRE_PROFILES

    def test_rocksteady_exists(self):
        assert "rocksteady" in GENRE_PROFILES

    def test_dub_exists(self):
        assert "dub" in GENRE_PROFILES

    @pytest.mark.parametrize(
        "variant",
        [
            "ska",
            "ska_first_wave",
            "ska_2tone",
            "ska_third_wave",
            "ska_punk",
            "ska_jazz",
            "rocksteady",
            "dub",
        ],
    )
    def test_all_ska_variants_transform(self, variant):
        song = Song(title="Test", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(name="melody", instrument="trumpet", volume=0.6))
        tr.extend(scale("C", "major", 5, length=8))
        ch = song.add_track(Track(name="chords", instrument="guitar_electric"))
        ch.add(Chord("C", "maj", 4, duration=8.0))
        result = genre_transform(song, variant)
        assert result is not None
        assert len(result.tracks) > 0

    def test_ska_punk_is_fast(self):
        assert GENRE_PROFILES["ska_punk"].default_bpm >= 190

    def test_rocksteady_is_slower(self):
        assert GENRE_PROFILES["rocksteady"].default_bpm < GENRE_PROFILES["ska"].default_bpm

    def test_dub_has_heavy_bass(self):
        assert GENRE_PROFILES["dub"].volumes.get("bass", 0) >= 0.7

    def test_ska_2tone_has_rimshot(self):
        assert GENRE_PROFILES["ska_2tone"].articulations.get("snare") == "rimshot"

    def test_ska_jazz_has_swing(self):
        assert GENRE_PROFILES["ska_jazz"].swing > 0

    def test_ska_punk_has_power_chords(self):
        hmap = GENRE_PROFILES["ska_punk"].harmony_map
        assert hmap.get("maj") == "power5"
        assert hmap.get("min") == "power5"


class TestSkaDrumPattern:
    def test_traditional_pattern(self):
        drums = ska_drum_pattern(bars=1, style="traditional")
        assert "kick" in drums
        assert "snare" in drums
        assert "hat" in drums
        assert len(drums["kick"]) == 16

    def test_traditional_kick_on_1_and_3(self):
        drums = ska_drum_pattern(bars=1, style="traditional")
        kick = drums["kick"]
        assert kick[0].pitch is not None  # beat 1
        assert kick[8].pitch is not None  # beat 3

    def test_traditional_snare_on_2_and_4(self):
        drums = ska_drum_pattern(bars=1, style="traditional")
        snare = drums["snare"]
        assert snare[4].pitch is not None  # beat 2
        assert snare[12].pitch is not None  # beat 4

    def test_traditional_hat_offbeat_only(self):
        drums = ska_drum_pattern(bars=1, style="traditional")
        hat = drums["hat"]
        # Offbeats at steps 2, 6, 10, 14
        assert hat[2].pitch is not None
        assert hat[6].pitch is not None
        assert hat[10].pitch is not None
        assert hat[14].pitch is not None
        # Downbeats should be rests
        assert hat[0].pitch is None
        assert hat[4].pitch is None

    def test_two_tone_has_rimshot(self):
        drums = ska_drum_pattern(bars=1, style="two_tone")
        snare = drums["snare"]
        snare_hits = [n for n in snare if n.pitch is not None]
        assert len(snare_hits) > 0
        assert snare_hits[0].articulation == "rimshot"

    def test_ska_punk_faster_hat(self):
        drums = ska_drum_pattern(bars=1, style="ska_punk")
        hat = drums["hat"]
        hat_hits = sum(1 for n in hat if n.pitch is not None)
        # Ska-punk has straight 8ths (all 16 slots hit)
        assert hat_hits == 16

    def test_ska_punk_four_on_floor_kick(self):
        drums = ska_drum_pattern(bars=1, style="ska_punk")
        kick = drums["kick"]
        kick_hits = [i for i, n in enumerate(kick) if n.pitch is not None]
        assert 0 in kick_hits  # beat 1
        assert 4 in kick_hits  # beat 2
        assert 8 in kick_hits  # beat 3
        assert 12 in kick_hits  # beat 4


class TestSkankPattern:
    def test_traditional_skank(self):
        result = skank_pattern("C", "maj", bars=1, style="traditional")
        assert len(result) == 16
        # Offbeats should have notes, downbeats should be rests
        assert result[2].pitch is not None  # first offbeat
        assert result[0].pitch is None  # first downbeat

    def test_traditional_skank_staccato(self):
        result = skank_pattern("C", "maj", bars=1, style="traditional")
        hits = [n for n in result if n.pitch is not None]
        assert all(h.articulation == "staccato" for h in hits)

    def test_two_tone_skank(self):
        result = skank_pattern("A", "min", bars=1, style="two_tone")
        hits = [n for n in result if n.pitch is not None]
        assert len(hits) == 4  # four offbeats per bar

    def test_ska_punk_has_ghost_mutes(self):
        result = skank_pattern("E", "power5", bars=1, style="ska_punk")
        muted = [n for n in result if n.pitch is not None and n.articulation == "muted"]
        assert len(muted) > 0, "Ska-punk skank should have ghost mutes on downbeats"

    def test_multiple_bars(self):
        result = skank_pattern("G", "maj", bars=4, style="traditional")
        assert len(result) == 64  # 16 steps x 4 bars


class TestSkaBassLine:
    def test_walking_style(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")]
        bass = ska_bass_line(prog, style="walking", seed=42)
        assert len(bass) == 16  # 4 notes per chord x 4 chords
        assert all(n.pitch is not None for n in bass)

    def test_rocksteady_style(self):
        prog = [("A", "min")] * 4
        bass = ska_bass_line(prog, style="rocksteady")
        assert len(bass) == 16

    def test_ska_punk_style(self):
        prog = [("E", "min")] * 2
        bass = ska_bass_line(prog, style="ska_punk")
        assert len(bass) == 16  # 8 notes per chord x 2 chords
        # 8th notes should be 0.5 duration
        assert bass[0].duration == 0.5

    def test_seed_reproducibility(self):
        prog = [("C", "maj")] * 4
        bass1 = ska_bass_line(prog, style="walking", seed=42)
        bass2 = ska_bass_line(prog, style="walking", seed=42)
        pitches1 = [n.pitch for n in bass1]
        pitches2 = [n.pitch for n in bass2]
        assert pitches1 == pitches2


class TestSkaHornRiff:
    def test_stab_style(self):
        result = ska_horn_riff("C", "maj", 5, bars=1, style="stab", seed=42)
        assert len(result) > 0
        hits = [n for n in result if n.pitch is not None]
        assert len(hits) > 0
        # Stabs should be staccato
        assert all(h.articulation == "staccato" for h in hits)

    def test_riff_style(self):
        result = ska_horn_riff("G", "dom7", 5, bars=1, style="riff")
        assert len(result) > 0

    def test_fanfare_style(self):
        result = ska_horn_riff("C", "maj", 5, bars=1, style="fanfare")
        assert len(result) > 0
        # Fanfare ends on a long note
        pitched = [n for n in result if n.pitch is not None]
        assert pitched[-1].duration >= 1.5


class TestSkaGrooveTemplates:
    def test_ska_groove_exists(self):
        from code_music.theory.rhythm import groove_template

        t = groove_template("ska")
        assert len(t) == 16

    def test_rocksteady_groove_exists(self):
        from code_music.theory.rhythm import groove_template

        t = groove_template("rocksteady")
        assert len(t) == 16

    def test_dub_groove_exists(self):
        from code_music.theory.rhythm import groove_template

        t = groove_template("dub")
        assert len(t) == 16


class TestSkaIntegration:
    def test_full_ska_song_renders(self):
        song = Song(title="Ska Test", bpm=168, sample_rate=22050)
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")]

        bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
        bass.extend(ska_bass_line(prog, style="walking", seed=42))

        skank = song.add_track(Track(name="skank", instrument="guitar_electric", volume=0.5))
        for root, shape in prog:
            skank.extend(skank_pattern(root, shape, style="traditional", bars=1))

        horns = song.add_track(Track(name="horns", instrument="trumpet", volume=0.5))
        horns.extend(ska_horn_riff("C", "maj", 5, bars=4, style="stab", seed=42))

        drums = ska_drum_pattern(bars=4, style="traditional")
        kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.6))
        kick.extend(drums["kick"])

        audio = song.render()
        assert audio.shape[0] > 0
        assert audio.shape[1] == 2

    def test_transform_pop_to_all_ska_variants(self):
        song = Song(title="Pop", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(name="melody", instrument="sawtooth"))
        tr.extend(scale("C", "major", 5, length=8))
        ch = song.add_track(Track(name="chords", instrument="piano"))
        ch.add(Chord("C", "maj", 4, duration=8.0))

        for variant in [
            "ska",
            "ska_first_wave",
            "ska_2tone",
            "ska_third_wave",
            "ska_punk",
            "ska_jazz",
            "rocksteady",
            "dub",
        ]:
            result = genre_transform(song, variant)
            assert result.bpm > 0, f"{variant} has zero BPM"
