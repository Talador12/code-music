"""Tests for v170 genre infrastructure: jazz, blues, funk, Latin, big band, lofi patterns."""

import pytest

from code_music.engine import CHORD_SHAPES, Note, Chord, Song, Track, scale


# ---------------------------------------------------------------------------
# Genre-specific chord shapes
# ---------------------------------------------------------------------------


class TestGenreChords:
    def test_blues_chords(self):
        assert "blues_maj" in CHORD_SHAPES
        assert "dom7#9" in CHORD_SHAPES

    def test_funk_chords(self):
        assert "min7_funk" in CHORD_SHAPES
        assert "dom7_funk" in CHORD_SHAPES

    def test_neosoul_chords(self):
        assert "maj9#11" in CHORD_SHAPES
        assert "min11_neo" in CHORD_SHAPES
        assert "dom7#9#5" in CHORD_SHAPES
        assert "maj7#5" in CHORD_SHAPES

    def test_bossa_chords(self):
        assert "6_9" in CHORD_SHAPES
        assert "min6_9" in CHORD_SHAPES
        assert "dom7b9_latin" in CHORD_SHAPES

    def test_lofi_chords(self):
        assert "maj7_open" in CHORD_SHAPES
        assert "min7_open" in CHORD_SHAPES
        assert "add9_open" in CHORD_SHAPES
        assert "sus4_add9" in CHORD_SHAPES

    def test_big_band_chords(self):
        assert "dom13" in CHORD_SHAPES
        assert "dom13_shell" in CHORD_SHAPES

    def test_genre_chords_render(self):
        genre_shapes = [
            "dom7#9",
            "min7_funk",
            "maj9#11",
            "6_9",
            "maj7_open",
            "dom13",
            "dom7_drop24",
            "min_add11",
            "blues_maj",
        ]
        for shape in genre_shapes:
            c = Chord("C", shape, 4)
            notes = c.notes
            assert len(notes) > 0, f"{shape} produced no notes"


# ---------------------------------------------------------------------------
# Clave and Latin patterns
# ---------------------------------------------------------------------------


class TestLatinPatterns:
    def test_clave_son_32(self):
        from code_music.theory.rhythm import clave_pattern

        pattern = clave_pattern("son_32", bars=1)
        assert len(pattern) == 16
        hits = sum(1 for n in pattern if n.pitch is not None)
        assert hits == 5  # son clave has 5 hits

    def test_clave_son_23(self):
        from code_music.theory.rhythm import clave_pattern

        pattern = clave_pattern("son_23", bars=1)
        hits = sum(1 for n in pattern if n.pitch is not None)
        assert hits == 5

    def test_clave_rumba(self):
        from code_music.theory.rhythm import clave_pattern

        pattern = clave_pattern("rumba_32", bars=1)
        hits = sum(1 for n in pattern if n.pitch is not None)
        assert hits == 5

    def test_clave_bossa(self):
        from code_music.theory.rhythm import clave_pattern

        pattern = clave_pattern("bossa", bars=1)
        assert len(pattern) == 16

    def test_clave_invalid(self):
        from code_music.theory.rhythm import clave_pattern

        with pytest.raises(ValueError):
            clave_pattern("nonexistent")

    def test_cascara_32(self):
        from code_music.theory.rhythm import cascara_pattern

        pattern = cascara_pattern("cascara_32", bars=1)
        assert len(pattern) == 16
        hits = sum(1 for n in pattern if n.pitch is not None)
        assert hits > 8  # cascara is dense

    def test_montuno(self):
        from code_music.theory.rhythm import montuno_pattern

        pattern = montuno_pattern("C", "min7", octave=4, bars=1)
        assert len(pattern) == 8
        assert all(n.pitch is not None for n in pattern)

    def test_bossa_nova_pattern(self):
        from code_music.theory.rhythm import bossa_nova_pattern

        drums = bossa_nova_pattern(bars=2)
        assert "kick" in drums
        assert "snare" in drums
        assert "hat" in drums
        assert len(drums["kick"]) == 32  # 16 steps x 2 bars


# ---------------------------------------------------------------------------
# Funk patterns
# ---------------------------------------------------------------------------


class TestFunkPatterns:
    def test_funk_drum_pattern(self):
        from code_music.theory.rhythm import funk_drum_pattern

        drums = funk_drum_pattern(bars=1, seed=42)
        assert "kick" in drums
        assert "snare" in drums
        assert "hat" in drums
        assert len(drums["kick"]) == 16

    def test_funk_ghost_notes(self):
        from code_music.theory.rhythm import funk_drum_pattern

        drums = funk_drum_pattern(bars=1, ghost_velocity=0.25, seed=42)
        snare = drums["snare"]
        ghost_count = sum(1 for n in snare if n.pitch is not None and n.velocity < 0.4)
        assert ghost_count > 0, "Funk snare should have ghost notes"


# ---------------------------------------------------------------------------
# Blues patterns
# ---------------------------------------------------------------------------


class TestBluesPatterns:
    def test_shuffle_drum_pattern(self):
        from code_music.theory.rhythm import shuffle_drum_pattern

        drums = shuffle_drum_pattern(bars=1, style="blues")
        assert "kick" in drums
        assert "snare" in drums
        assert "hat" in drums
        assert len(drums["kick"]) == 12  # triplet subdivisions

    def test_shuffle_boogie(self):
        from code_music.theory.rhythm import shuffle_drum_pattern

        drums = shuffle_drum_pattern(bars=1, style="boogie")
        kick = drums["kick"]
        kick_hits = sum(1 for n in kick if n.pitch is not None)
        assert kick_hits >= 4  # boogie has more kick hits

    def test_blues_bass_shuffle(self):
        from code_music.theory import bass_line_blues

        prog = [("E", "dom7"), ("A", "dom7"), ("E", "dom7"), ("B", "dom7")]
        bass = bass_line_blues(prog, style="shuffle")
        assert len(bass) > 0
        assert any(n.pitch is not None for n in bass)

    def test_blues_bass_boogie(self):
        from code_music.theory import bass_line_blues

        prog = [("C", "dom7")] * 4
        bass = bass_line_blues(prog, style="boogie")
        assert len(bass) == 32  # 8 notes per chord x 4 chords

    def test_blues_bass_walking(self):
        from code_music.theory import bass_line_blues

        prog = [("G", "dom7")] * 4
        bass = bass_line_blues(prog, style="walking", seed=42)
        assert len(bass) == 16  # 4 notes per chord x 4 chords


# ---------------------------------------------------------------------------
# Big band patterns
# ---------------------------------------------------------------------------


class TestBigBandPatterns:
    def test_big_band_drums_swing(self):
        from code_music.theory.rhythm import big_band_drum_pattern

        drums = big_band_drum_pattern(bars=2, feel="swing")
        assert "ride" in drums
        assert "hat_foot" in drums
        assert "kick" in drums
        assert "snare" in drums
        assert len(drums["ride"]) == 16  # 8 steps x 2 bars

    def test_big_band_drums_latin(self):
        from code_music.theory.rhythm import big_band_drum_pattern

        drums = big_band_drum_pattern(bars=1, feel="latin")
        assert len(drums["ride"]) == 8

    def test_big_band_orchestrate(self):
        from code_music.symphony import orchestrate_big_band

        melody = scale("Bb", "major", 5, length=8)
        mvt = orchestrate_big_band(melody, key="Bb", style="swing", seed=42)
        assert len(mvt.parts) >= 10  # trumpets + trombones + saxes + rhythm
        assert "trumpet_1" in mvt.parts
        assert "alto_sax_1" in mvt.parts
        assert "piano" in mvt.parts
        assert "bass" in mvt.parts

    def test_big_band_bebop(self):
        from code_music.symphony import orchestrate_big_band

        melody = [Note("C", 5, 0.5)] * 8
        mvt = orchestrate_big_band(melody, style="bebop", seed=42)
        assert "bari_sax" in mvt.parts


# ---------------------------------------------------------------------------
# Lofi patterns
# ---------------------------------------------------------------------------


class TestLofiPatterns:
    def test_lofi_drum_pattern(self):
        from code_music.theory.rhythm import lofi_drum_pattern

        drums = lofi_drum_pattern(bars=1, seed=42)
        assert "kick" in drums
        assert "snare" in drums
        assert "hat" in drums

    def test_lofi_bass_line(self):
        from code_music.theory import bass_line_lofi

        prog = [("D", "maj7"), ("F#", "min7"), ("G", "maj7"), ("E", "min7")]
        bass = bass_line_lofi(prog, seed=42)
        assert len(bass) > 0
        # Lofi bass is sparse - should have rests
        rest_count = sum(1 for n in bass if n.pitch is None)
        assert rest_count > 0, "Lofi bass should have rests for space"


# ---------------------------------------------------------------------------
# Groove templates
# ---------------------------------------------------------------------------


class TestGrooveTemplates:
    def test_new_groove_templates(self):
        from code_music.theory.rhythm import groove_template

        new_grooves = [
            "funk_tight",
            "funk_loose",
            "afrobeat",
            "reggae",
            "neo_soul",
            "lofi",
            "samba",
            "salsa",
            "swing_heavy",
            "big_band",
        ]
        for name in new_grooves:
            template = groove_template(name)
            assert len(template) == 16, f"{name} should have 16 values"
            assert isinstance(template, list)


# ---------------------------------------------------------------------------
# Genre progression templates
# ---------------------------------------------------------------------------


class TestGenreProgressions:
    def test_funk_templates(self):
        from code_music.theory._core import _GENRE_TEMPLATES

        assert "funk" in _GENRE_TEMPLATES
        assert len(_GENRE_TEMPLATES["funk"]) >= 3

    def test_latin_templates(self):
        from code_music.theory._core import _GENRE_TEMPLATES

        assert "latin" in _GENRE_TEMPLATES

    def test_lofi_templates(self):
        from code_music.theory._core import _GENRE_TEMPLATES

        assert "lofi" in _GENRE_TEMPLATES

    def test_gospel_templates(self):
        from code_music.theory._core import _GENRE_TEMPLATES

        assert "gospel" in _GENRE_TEMPLATES

    def test_bossa_nova_templates(self):
        from code_music.theory._core import _GENRE_TEMPLATES

        assert "bossa_nova" in _GENRE_TEMPLATES

    def test_big_band_templates(self):
        from code_music.theory._core import _GENRE_TEMPLATES

        assert "big_band" in _GENRE_TEMPLATES

    def test_r_and_b_templates(self):
        from code_music.theory._core import _GENRE_TEMPLATES

        assert "r&b" in _GENRE_TEMPLATES
