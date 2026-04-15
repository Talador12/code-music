"""Tests for v170 features: expanded instruments, effects, chords, dynamics, symphony."""

import numpy as np
import pytest

from code_music.engine import (
    CHORD_SHAPES,
    PPPP,
    PPP,
    PP,
    P,
    MP,
    MF,
    F,
    FF,
    FFF,
    FFFF,
    SFZ,
    FP,
    VELOCITY_CURVES,
    Chord,
    Note,
    Song,
    Track,
    crescendo,
    double_octave,
    dynamics,
    octave_down,
    octave_up,
    scale,
    transpose,
    velocity_curve,
)
from code_music.synth import Synth


# ---------------------------------------------------------------------------
# New chord shapes
# ---------------------------------------------------------------------------


class TestNewChords:
    def test_quintal_shape(self):
        assert "quintal" in CHORD_SHAPES
        assert CHORD_SHAPES["quintal"] == [0, 7, 14, 21]

    def test_quartal5_shape(self):
        assert "quartal5" in CHORD_SHAPES
        assert len(CHORD_SHAPES["quartal5"]) == 5

    def test_polychord_shapes(self):
        assert "poly_C_D" in CHORD_SHAPES
        assert "poly_C_Gb" in CHORD_SHAPES
        assert "poly_C_E" in CHORD_SHAPES

    def test_cluster_shapes(self):
        assert "cluster3" in CHORD_SHAPES
        assert CHORD_SHAPES["cluster3"] == [0, 1, 2]
        assert "cluster4" in CHORD_SHAPES
        assert "cluster5" in CHORD_SHAPES
        assert "diatonic_cluster3" in CHORD_SHAPES
        assert "diatonic_cluster4" in CHORD_SHAPES

    def test_slash_chord_shapes(self):
        assert "maj_inv1_bass" in CHORD_SHAPES
        assert "maj_inv2_bass" in CHORD_SHAPES
        assert "min_inv1_bass" in CHORD_SHAPES

    def test_altered_dominant_shapes(self):
        assert "7b5" in CHORD_SHAPES
        assert "7#5" in CHORD_SHAPES
        assert "7b5b9" in CHORD_SHAPES
        assert "7#5#9" in CHORD_SHAPES
        assert "7b13" in CHORD_SHAPES

    def test_extended_jazz_shapes(self):
        assert "min_maj7" in CHORD_SHAPES
        assert "9sus4" in CHORD_SHAPES
        assert "7sus2" in CHORD_SHAPES

    def test_spectral_shapes(self):
        assert "harmonic7" in CHORD_SHAPES
        assert "harmonic9" in CHORD_SHAPES
        assert "spectral_cluster" in CHORD_SHAPES

    def test_messiaen_shapes(self):
        assert "messiaen_mode2" in CHORD_SHAPES
        assert "messiaen_mode3" in CHORD_SHAPES

    def test_mu_chord(self):
        assert "mu" in CHORD_SHAPES
        assert "mu7" in CHORD_SHAPES
        assert CHORD_SHAPES["mu"] == [0, 2, 4, 7]

    def test_chord_renders_notes(self):
        for shape in ["quintal", "cluster3", "poly_C_D", "7b5", "min_maj7", "harmonic7", "mu"]:
            c = Chord("C", shape, 4)
            notes = c.notes
            assert len(notes) > 0, f"{shape} produced no notes"
            assert all(n.midi is not None for n in notes), f"{shape} has None midi"


# ---------------------------------------------------------------------------
# Dynamics constants
# ---------------------------------------------------------------------------


class TestDynamics:
    def test_dynamic_ordering(self):
        assert PPPP < PPP < PP < P < MP < MF < F < FF < FFF < FFFF

    def test_sfz_is_max(self):
        assert SFZ == 1.0

    def test_fp_is_soft(self):
        assert FP < MF

    def test_velocity_curves_exist(self):
        for name in [
            "linear",
            "exponential",
            "logarithmic",
            "s_curve",
            "piano",
            "organ",
            "percussion",
        ]:
            assert name in VELOCITY_CURVES
            fn = VELOCITY_CURVES[name]
            assert callable(fn)
            assert 0.0 <= fn(0.5) <= 1.0

    def test_dynamics_function(self):
        notes = scale("C", "major", 4, length=4)
        loud = dynamics(notes, FF)
        assert all(n.velocity == FF for n in loud if n.pitch is not None)

    def test_velocity_curve_function(self):
        notes = [Note("C", 4, 1.0, velocity=0.5) for _ in range(4)]
        curved = velocity_curve(notes, "exponential")
        assert len(curved) == 4
        assert curved[0].velocity == pytest.approx(0.25, abs=0.01)


# ---------------------------------------------------------------------------
# Pitch range utilities
# ---------------------------------------------------------------------------


class TestPitchRange:
    def test_octave_up(self):
        notes = [Note("C", 4, 1.0)]
        up = octave_up(notes)
        assert up[0].pitch == notes[0].midi + 12

    def test_octave_down(self):
        notes = [Note("C", 4, 1.0)]
        down = octave_down(notes)
        assert down[0].pitch == notes[0].midi - 12

    def test_octave_up_n(self):
        notes = [Note("C", 4, 1.0)]
        up2 = octave_up(notes, 2)
        assert up2[0].pitch == notes[0].midi + 24

    def test_double_octave_both(self):
        notes = [Note("C", 4, 1.0)]
        doubled = double_octave(notes, "both")
        assert len(doubled) == 3  # original + up + down

    def test_double_octave_up(self):
        notes = [Note("C", 4, 1.0)]
        doubled = double_octave(notes, "up")
        assert len(doubled) == 2

    def test_double_octave_preserves_rests(self):
        notes = [Note.rest(1.0)]
        doubled = double_octave(notes)
        assert len(doubled) == 1


# ---------------------------------------------------------------------------
# New instruments
# ---------------------------------------------------------------------------


class TestNewInstruments:
    @pytest.fixture
    def synth(self):
        return Synth(sample_rate=22050)

    def test_new_presets_exist(self):
        new_instruments = [
            "cor_anglais",
            "bass_clarinet",
            "contrabassoon",
            "alto_flute",
            "english_horn",
            "soprano_sax",
            "tenor_sax",
            "bari_sax",
            "euphonium",
            "cornet",
            "flugelhorn",
            "piccolo_trumpet",
            "bass_trombone",
            "horn_section",
            "viola",
            "string_section",
            "string_tremolo",
            "string_harmonics",
            "erhu",
            "shamisen",
            "oud",
            "bouzouki",
            "dulcimer",
            "guzheng",
            "balalaika",
            "ukulele",
            "mandolin",
            "steelpan",
            "kalimba",
            "gamelan",
            "didgeridoo",
            "bagpipe",
            "harmonica",
            "accordion",
            "bandoneon",
            "cajon",
            "bongo",
            "conga",
            "shaker",
            "tambourine",
            "cowbell",
            "woodblock",
            "triangle_perc",
            "timbales",
            "surdo",
            "pulse",
            "sync_lead",
            "trance_lead",
            "chiptune",
            "ambient_pad",
            "dark_pad",
            "glass_pad",
            "warm_pad",
            "poly_synth",
            "fm_keys",
            "fm_pad",
            "drums_rimshot",
            "drums_open_hat",
            "drums_low_tom",
            "drums_floor_tom",
            "drums_splash",
            "drums_china",
            "drums_ghost_snare",
            "drums_brush",
        ]
        for name in new_instruments:
            assert name in Synth.PRESETS, f"Missing preset: {name}"

    def test_new_instruments_render(self, synth):
        sample_presets = [
            "cor_anglais",
            "erhu",
            "shamisen",
            "cajon",
            "chiptune",
            "ambient_pad",
            "drums_brush",
        ]
        for name in sample_presets:
            note = Note("A", 4, 0.5, velocity=0.7)
            n_samples = int(0.5 * 60.0 / 120.0 * synth.sample_rate)
            preset = synth.PRESETS[name]
            audio = synth._render_note(note, n_samples, preset, name)
            assert len(audio) == n_samples
            assert np.max(np.abs(audio)) > 0, f"{name} produced silence"


# ---------------------------------------------------------------------------
# New effects
# ---------------------------------------------------------------------------


class TestNewEffects:
    @pytest.fixture
    def stereo_signal(self):
        sr = 22050
        t = np.linspace(0, 0.5, sr // 2)
        mono = np.sin(2 * np.pi * 440 * t) * 0.5
        return np.column_stack([mono, mono]).astype(np.float64), sr

    def test_shimmer_reverb(self, stereo_signal):
        from code_music.effects import shimmer_reverb

        samples, sr = stereo_signal
        out = shimmer_reverb(samples, sr, wet=0.3)
        assert out.shape == samples.shape
        assert np.max(np.abs(out)) > 0

    def test_spring_reverb(self, stereo_signal):
        from code_music.effects import spring_reverb

        samples, sr = stereo_signal
        out = spring_reverb(samples, sr, wet=0.3)
        assert out.shape == samples.shape

    def test_rotary_speaker_slow(self, stereo_signal):
        from code_music.effects import rotary_speaker

        samples, sr = stereo_signal
        out = rotary_speaker(samples, sr, speed="slow")
        assert out.shape == samples.shape

    def test_rotary_speaker_fast(self, stereo_signal):
        from code_music.effects import rotary_speaker

        samples, sr = stereo_signal
        out = rotary_speaker(samples, sr, speed="fast")
        assert out.shape == samples.shape

    def test_tape_wow_flutter(self, stereo_signal):
        from code_music.effects import tape_wow_flutter

        samples, sr = stereo_signal
        out = tape_wow_flutter(samples, sr)
        assert out.shape == samples.shape

    def test_lofi_vinyl(self, stereo_signal):
        from code_music.effects import lofi_vinyl

        samples, sr = stereo_signal
        out = lofi_vinyl(samples, sr, crackle=0.02, hiss=0.01)
        assert out.shape == samples.shape

    def test_harmonic_exciter(self, stereo_signal):
        from code_music.effects import harmonic_exciter

        samples, sr = stereo_signal
        out = harmonic_exciter(samples, sr)
        assert out.shape == samples.shape

    def test_pitch_shift(self, stereo_signal):
        from code_music.effects import pitch_shift

        samples, sr = stereo_signal
        out = pitch_shift(samples, sr, semitones=7)
        assert out.shape == samples.shape

    def test_pitch_shift_zero(self, stereo_signal):
        from code_music.effects import pitch_shift

        samples, sr = stereo_signal
        out = pitch_shift(samples, sr, semitones=0)
        np.testing.assert_array_equal(out, samples)


# ---------------------------------------------------------------------------
# Performance effects
# ---------------------------------------------------------------------------


class TestPerformanceEffects:
    def test_fermata(self):
        from code_music.theory.rhythm import fermata

        n = Note("C", 4, 1.0)
        held = fermata(n, stretch=2.0)
        assert held.duration == 2.0
        assert held.pitch == "C"

    def test_fermata_rest(self):
        from code_music.theory.rhythm import fermata

        n = Note.rest(1.0)
        held = fermata(n, stretch=2.0)
        assert held.duration == 2.0
        assert held.pitch is None

    def test_caesura(self):
        from code_music.theory.rhythm import caesura

        rest = caesura(1.5)
        assert rest.pitch is None
        assert rest.duration == 1.5

    def test_grand_pause(self):
        from code_music.theory.rhythm import grand_pause

        gp = grand_pause(3.0)
        assert gp.pitch is None
        assert gp.duration == 3.0

    def test_a_tempo(self):
        from code_music.theory.rhythm import a_tempo

        notes = [Note("C", 4, 2.0), Note("E", 4, 2.0)]  # at 60bpm (slow)
        restored = a_tempo(notes, target_bpm=120, current_bpm=60)
        assert restored[0].duration == pytest.approx(1.0)
        assert restored[1].duration == pytest.approx(1.0)

    def test_tempo_curve(self):
        from code_music.theory.rhythm import tempo_curve

        notes = [Note("C", 4, 1.0)] * 4
        curved = tempo_curve(notes, [120, 120, 60, 60], base_bpm=120)
        assert len(curved) == 4
        assert curved[0].duration == pytest.approx(1.0, abs=0.01)
        assert curved[3].duration == pytest.approx(2.0, abs=0.01)

    def test_morendo(self):
        from code_music.theory.rhythm import morendo

        notes = [Note("C", 4, 1.0, velocity=0.8)] * 4
        dying = morendo(notes)
        assert len(dying) == 4
        assert dying[0].velocity > dying[-1].velocity
        assert dying[0].duration < dying[-1].duration

    def test_calando(self):
        from code_music.theory.rhythm import calando

        notes = [Note("C", 4, 1.0, velocity=0.7)] * 4
        calmed = calando(notes, amount=0.5)
        assert len(calmed) == 4
        assert calmed[-1].duration > calmed[0].duration


# ---------------------------------------------------------------------------
# Symphony system
# ---------------------------------------------------------------------------


class TestSymphony:
    def test_create_symphony(self):
        from code_music.symphony import Symphony

        sym = Symphony(title="Test Symphony", composer="Test")
        assert sym.title == "Test Symphony"
        assert len(sym.movements) == 0

    def test_add_movement(self):
        from code_music.symphony import Symphony

        sym = Symphony(title="Test")
        mvt = sym.add_movement("I. Allegro", bpm=132, key="C")
        assert len(sym.movements) == 1
        assert mvt.bpm == 132

    def test_add_part(self):
        from code_music.symphony import Symphony

        sym = Symphony()
        mvt = sym.add_movement("I", bpm=120)
        fl = mvt.add_part("flute", "flute")
        fl.add(Note("C", 5, 1.0))
        fl.add(Note("D", 5, 1.0))
        assert "flute" in mvt.parts
        assert len(mvt.parts["flute"].notes) == 2

    def test_render_symphony(self):
        from code_music.symphony import Symphony

        sym = Symphony(title="Mini Symphony")
        mvt1 = sym.add_movement("I", bpm=120)
        vln = mvt1.add_part("violin_1", "violin")
        vln.extend(scale("C", "major", 5, length=8))
        song = sym.render()
        assert len(song.tracks) == 1
        assert song.title == "Mini Symphony"

    def test_render_multi_movement(self):
        from code_music.symphony import Symphony

        sym = Symphony(title="Two Movements")
        mvt1 = sym.add_movement("I", bpm=120)
        mvt1.add_part("violin_1", "violin").extend([Note("C", 5, 1.0)] * 4)
        mvt2 = sym.add_movement("II", bpm=80)
        mvt2.add_part("violin_1", "violin").extend([Note("G", 4, 2.0)] * 4)
        song = sym.render()
        assert len(song.tracks) == 1
        total_beats = song.tracks[0].total_beats
        assert total_beats > 8  # both movements + gap

    def test_movement_to_song(self):
        from code_music.symphony import Movement

        mvt = Movement(title="Test", bpm=100)
        mvt.add_part("flute", "flute").extend([Note("A", 5, 1.0)] * 4)
        mvt.add_part("cello", "cello").extend([Note("A", 3, 2.0)] * 2)
        song = mvt.to_song()
        assert len(song.tracks) == 2
        assert song.bpm == 100

    def test_transposing_instrument(self):
        from code_music.symphony import Part

        part = Part(name="clarinet", instrument="clarinet")
        part.add(Note("C", 4, 1.0))  # concert C4
        written = part.transpose_for_score()
        assert len(written) == 1
        # Bb clarinet: concert C4 = written D4
        assert written[0].midi == Note("C", 4, 1.0).midi + 2

    def test_score_ordering(self):
        from code_music.symphony import score_sort_key

        assert score_sort_key("flute") < score_sort_key("trumpet")
        assert score_sort_key("trumpet") < score_sort_key("violin_1")

    def test_get_family(self):
        from code_music.symphony import get_family

        assert get_family("flute") == "woodwinds"
        assert get_family("trumpet") == "brass"
        assert get_family("violin") == "strings"
        assert get_family("timpani") == "percussion"
        assert get_family("piano") == "keyboards"

    def test_export_musicxml(self, tmp_path):
        from code_music.symphony import Symphony

        sym = Symphony(title="Export Test", composer="Test")
        mvt = sym.add_movement("I", bpm=120)
        mvt.add_part("flute", "flute").extend([Note("C", 5, 1.0)] * 4)
        mvt.add_part("violin_1", "violin").extend([Note("A", 4, 1.0)] * 4)
        path = str(tmp_path / "test_score.xml")
        result = sym.export_score(path, format="musicxml")
        assert result.endswith(".xml")
        content = open(result).read()
        assert "<score-partwise" in content
        assert "Export Test" in content

    def test_export_lilypond(self, tmp_path):
        from code_music.symphony import Symphony

        sym = Symphony(title="Lily Test", composer="Test")
        mvt = sym.add_movement("I", bpm=120)
        mvt.add_part("flute", "flute").extend([Note("C", 5, 1.0)] * 4)
        path = str(tmp_path / "test_score.ly")
        result = sym.export_score(path, format="lilypond")
        assert result.endswith(".ly")
        content = open(result).read()
        assert "Lily Test" in content
        assert "\\score" in content

    def test_export_part(self, tmp_path):
        from code_music.symphony import Symphony

        sym = Symphony(title="Part Test")
        mvt = sym.add_movement("I", bpm=120)
        mvt.add_part("clarinet", "clarinet").extend([Note("C", 4, 1.0)] * 4)
        path = str(tmp_path / "clarinet_part.xml")
        result = sym.export_part("clarinet", path)
        assert "clarinet_part" in result

    def test_orchestrate_romantic(self):
        from code_music.symphony import orchestrate

        melody = scale("C", "major", 5, length=8)
        mvt = orchestrate(melody, key="C", style="romantic", seed=42)
        assert len(mvt.parts) >= 5
        assert "violin_1" in mvt.parts
        assert "cello" in mvt.parts

    def test_orchestrate_chamber(self):
        from code_music.symphony import orchestrate

        melody = [Note("C", 5, 1.0)] * 4
        mvt = orchestrate(melody, key="C", style="chamber", seed=42)
        assert len(mvt.parts) == 4
        assert "viola" in mvt.parts

    def test_instrument_range_check(self):
        from code_music.symphony import Part

        part = Part(name="piccolo", instrument="piccolo")
        part.add(Note("C", 6, 1.0))  # within range
        assert part.in_range()
        part.add(Note("C", 2, 1.0))  # way below range
        assert not part.in_range()


# ---------------------------------------------------------------------------
# Integration: full render with new features
# ---------------------------------------------------------------------------


class TestIntegration:
    def test_song_with_new_instruments(self):
        song = Song(title="v170 Instruments", bpm=120, sample_rate=22050)
        tr1 = song.add_track(Track(name="erhu", instrument="erhu", volume=0.6))
        tr1.extend([Note("A", 4, 1.0)] * 4)
        tr2 = song.add_track(Track(name="cajon", instrument="cajon", volume=0.7))
        tr2.extend([Note("C", 3, 0.5)] * 8)
        audio = song.render()
        assert audio.shape[0] > 0
        assert audio.shape[1] == 2

    def test_song_with_new_chords(self):
        song = Song(title="v170 Chords", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(name="pad", instrument="pad", volume=0.5))
        tr.add(Chord("C", "quintal", 3, duration=4.0))
        tr.add(Chord("C", "cluster3", 4, duration=2.0))
        tr.add(Chord("C", "mu", 4, duration=4.0))
        audio = song.render()
        assert np.max(np.abs(audio)) > 0

    def test_full_pipeline_dynamics(self):
        notes = scale("C", "major", 5, length=8)
        soft = dynamics(notes, PP)
        loud = dynamics(notes, FF)
        assert all(n.velocity == PP for n in soft if n.pitch is not None)
        assert all(n.velocity == FF for n in loud if n.pitch is not None)
        assert soft[0].velocity < loud[0].velocity
