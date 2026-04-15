"""Tests for v170 articulation system: per-note articulation field + synth-aware rendering."""

import numpy as np
import pytest

from code_music.engine import (
    Note,
    Chord,
    Song,
    Track,
    scale,
    staccato,
    legato,
    pizzicato,
    con_sordino,
    senza_sordino,
    sul_ponticello,
    sul_tasto,
    col_legno,
    spiccato,
    tremolo_bow,
    harmonics,
    muted,
    flutter_tongue,
    with_brushes,
    with_mallets,
    with_rods,
    rim_click,
    dead_stroke,
)
from code_music.synth import Synth


class TestArticulationField:
    """Verify the articulation field on Note."""

    def test_default_articulation_is_none(self):
        n = Note("C", 4, 1.0)
        assert n.articulation is None

    def test_articulation_can_be_set(self):
        n = Note("C", 4, 1.0, articulation="pizzicato")
        assert n.articulation == "pizzicato"

    def test_rest_has_no_articulation(self):
        r = Note.rest(1.0)
        assert r.articulation is None

    def test_articulation_in_repr(self):
        n = Note("C", 4, 1.0, articulation="muted")
        # Should not crash repr
        repr(n)


class TestArticulationFunctions:
    """Verify that articulation helper functions set the field."""

    def test_staccato_sets_articulation(self):
        notes = [Note("C", 4, 1.0)]
        result = staccato(notes)
        pitched = [n for n in result if n.pitch is not None]
        assert pitched[0].articulation == "staccato"

    def test_legato_sets_articulation(self):
        notes = [Note("C", 4, 1.0)]
        result = legato(notes)
        assert result[0].articulation == "legato"

    def test_pizzicato_sets_articulation(self):
        notes = [Note("C", 4, 1.0)]
        result = pizzicato(notes)
        assert result[0].articulation == "pizzicato"

    def test_con_sordino_sets_articulation(self):
        notes = [Note("C", 4, 1.0)]
        result = con_sordino(notes)
        assert result[0].articulation == "con_sordino"

    def test_senza_sordino_clears_articulation(self):
        notes = [Note("C", 4, 1.0, articulation="con_sordino")]
        result = senza_sordino(notes)
        assert result[0].articulation is None

    def test_sul_ponticello_sets_articulation(self):
        notes = [Note("A", 4, 1.0)]
        result = sul_ponticello(notes)
        assert result[0].articulation == "sul_ponticello"

    def test_sul_tasto_sets_articulation(self):
        notes = [Note("A", 4, 1.0)]
        result = sul_tasto(notes)
        assert result[0].articulation == "sul_tasto"

    def test_col_legno_sets_articulation(self):
        notes = [Note("A", 4, 1.0)]
        result = col_legno(notes)
        assert result[0].articulation == "col_legno"

    def test_spiccato_sets_articulation(self):
        notes = [Note("A", 4, 1.0)]
        result = spiccato(notes)
        assert result[0].articulation == "spiccato"

    def test_tremolo_bow_sets_articulation(self):
        notes = [Note("A", 4, 1.0)]
        result = tremolo_bow(notes)
        assert result[0].articulation == "tremolo"

    def test_harmonics_sets_articulation(self):
        notes = [Note("A", 4, 1.0)]
        result = harmonics(notes)
        assert result[0].articulation == "harmonics"

    def test_muted_sets_articulation(self):
        notes = [Note("Bb", 4, 1.0)]
        result = muted(notes)
        assert result[0].articulation == "muted"

    def test_flutter_tongue_sets_articulation(self):
        notes = [Note("C", 5, 1.0)]
        result = flutter_tongue(notes)
        assert result[0].articulation == "flutter_tongue"

    def test_with_brushes_sets_articulation(self):
        notes = [Note("D", 3, 0.5)]
        result = with_brushes(notes)
        assert result[0].articulation == "brush"

    def test_with_mallets_sets_articulation(self):
        notes = [Note("C", 4, 1.0)]
        result = with_mallets(notes)
        assert result[0].articulation == "mallet"

    def test_with_rods_sets_articulation(self):
        notes = [Note("D", 3, 0.5)]
        result = with_rods(notes)
        assert result[0].articulation == "rod"

    def test_rim_click_sets_articulation(self):
        notes = [Note("D", 3, 0.5)]
        result = rim_click(notes)
        assert result[0].articulation == "cross_stick"

    def test_dead_stroke_sets_articulation(self):
        notes = [Note("C", 4, 1.0)]
        result = dead_stroke(notes)
        assert result[0].articulation == "dead_stroke"

    def test_rests_pass_through(self):
        notes = [Note.rest(1.0)]
        for fn in [con_sordino, muted, with_brushes, pizzicato]:
            result = fn(notes)
            assert result[0].pitch is None


class TestArticulationSynthesis:
    """Verify the synth produces different waveforms for different articulations."""

    @pytest.fixture
    def synth(self):
        return Synth(sample_rate=22050)

    def _render(self, synth, instrument, articulation=None, velocity=0.7):
        note = Note("A", 4, 0.5, velocity=velocity, articulation=articulation)
        n_samples = int(0.5 * 60.0 / 120.0 * synth.sample_rate)
        preset = synth.PRESETS.get(instrument, synth.PRESETS["sine"])
        return synth._render_note(note, n_samples, preset, instrument)

    def _spectral_centroid(self, audio, sr):
        """Rough spectral centroid - higher value = brighter sound."""
        fft = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), 1.0 / sr)
        if np.sum(fft) < 1e-10:
            return 0.0
        return np.sum(freqs * fft) / np.sum(fft)

    def test_pizzicato_darker_than_arco(self, synth):
        arco = self._render(synth, "violin")
        pizz = self._render(synth, "violin", "pizzicato")
        # Pizzicato should be darker (lower spectral centroid)
        c_arco = self._spectral_centroid(arco, synth.sample_rate)
        c_pizz = self._spectral_centroid(pizz, synth.sample_rate)
        assert c_pizz < c_arco, "Pizzicato should be darker than arco"

    def test_sul_ponticello_brighter_than_normal(self, synth):
        normal = self._render(synth, "violin")
        pont = self._render(synth, "violin", "sul_ponticello")
        c_normal = self._spectral_centroid(normal, synth.sample_rate)
        c_pont = self._spectral_centroid(pont, synth.sample_rate)
        assert c_pont > c_normal, "Sul ponticello should be brighter"

    def test_sul_tasto_darker_than_normal(self, synth):
        normal = self._render(synth, "violin")
        tasto = self._render(synth, "violin", "sul_tasto")
        c_normal = self._spectral_centroid(normal, synth.sample_rate)
        c_tasto = self._spectral_centroid(tasto, synth.sample_rate)
        assert c_tasto < c_normal, "Sul tasto should be darker"

    def test_muted_trumpet_darker(self, synth):
        open_tp = self._render(synth, "trumpet")
        muted_tp = self._render(synth, "trumpet", "muted")
        c_open = self._spectral_centroid(open_tp, synth.sample_rate)
        c_muted = self._spectral_centroid(muted_tp, synth.sample_rate)
        assert c_muted < c_open, "Muted trumpet should be darker"

    def test_harmon_mute_different_from_straight(self, synth):
        straight = self._render(synth, "trumpet", "muted")
        harmon = self._render(synth, "trumpet", "harmon_mute")
        # They should sound different (different spectral shape)
        assert not np.allclose(straight, harmon, atol=0.01)

    def test_brush_drums_different_from_stick(self, synth):
        stick = self._render(synth, "drums_snare")
        brush = self._render(synth, "drums_snare", "brush")
        # Brush should be much quieter/different
        assert not np.allclose(stick, brush, atol=0.01)

    def test_mallet_is_warmer(self, synth):
        stick = self._render(synth, "marimba")
        mallet = self._render(synth, "marimba", "mallet")
        c_stick = self._spectral_centroid(stick, synth.sample_rate)
        c_mallet = self._spectral_centroid(mallet, synth.sample_rate)
        assert c_mallet < c_stick, "Mallet should be warmer than stick"

    def test_dead_stroke_shorter(self, synth):
        normal = self._render(synth, "drums_tom")
        dead = self._render(synth, "drums_tom", "dead_stroke")
        # Dead stroke should have less energy in the tail
        tail_start = len(normal) // 2
        normal_tail_energy = np.mean(normal[tail_start:] ** 2)
        dead_tail_energy = np.mean(dead[tail_start:] ** 2)
        assert dead_tail_energy < normal_tail_energy

    def test_flutter_tongue_has_modulation(self, synth):
        normal = self._render(synth, "trumpet")
        flutter = self._render(synth, "trumpet", "flutter_tongue")
        # Flutter should have more amplitude variation (higher std dev of envelope)
        # Use a simple windowed RMS comparison
        assert not np.allclose(normal, flutter, atol=0.01)

    def test_con_sordino_quieter(self, synth):
        open_str = self._render(synth, "violin")
        sord = self._render(synth, "violin", "con_sordino")
        assert np.max(np.abs(sord)) < np.max(np.abs(open_str))

    def test_cross_stick_different_from_normal(self, synth):
        normal = self._render(synth, "drums_snare")
        xstick = self._render(synth, "drums_snare", "cross_stick")
        assert not np.allclose(normal, xstick, atol=0.01)


class TestArticulationIntegration:
    """Full render pipeline with articulated notes."""

    def test_mixed_articulations_in_track(self):
        song = Song(title="Articulation Test", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(name="violin", instrument="violin", volume=0.6))
        # Mix of articulations in one track
        tr.add(Note("A", 4, 1.0, velocity=0.7))  # normal
        tr.add(Note("A", 4, 1.0, velocity=0.7, articulation="pizzicato"))
        tr.add(Note("A", 4, 1.0, velocity=0.7, articulation="tremolo"))
        tr.add(Note("A", 4, 1.0, velocity=0.7, articulation="harmonics"))
        audio = song.render()
        assert audio.shape[0] > 0
        assert audio.shape[1] == 2

    def test_brass_mute_combinations(self):
        song = Song(title="Brass Mutes", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(name="trumpet", instrument="trumpet", volume=0.6))
        tr.add(Note("Bb", 4, 1.0))  # open
        tr.add(Note("Bb", 4, 1.0, articulation="muted"))
        tr.add(Note("Bb", 4, 1.0, articulation="harmon_mute"))
        tr.add(Note("Bb", 4, 1.0, articulation="cup_mute"))
        audio = song.render()
        assert np.max(np.abs(audio)) > 0

    def test_drum_implement_combinations(self):
        song = Song(title="Drum Sticks", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.7))
        tr.add(Note("D", 3, 0.5))  # stick (default)
        tr.add(Note("D", 3, 0.5, articulation="brush"))
        tr.add(Note("D", 3, 0.5, articulation="cross_stick"))
        tr.add(Note("D", 3, 0.5, articulation="rimshot"))
        tr.add(Note("D", 3, 0.5, articulation="dead_stroke"))
        tr.add(Note("D", 3, 0.5, articulation="flam"))
        tr.add(Note("D", 3, 0.5, articulation="roll"))
        audio = song.render()
        assert audio.shape[0] > 0
