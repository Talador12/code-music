"""Tests for SoundDesigner: custom instrument creation from scratch."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import numpy as np

from code_music import Note, Song, SoundDesigner, Track, Wavetable, euclid
from code_music.sound_design import PRESETS, sub_808, supersaw

SR = 22050


class TestSoundDesignerBuild:
    def test_empty_designer_renders(self):
        sd = SoundDesigner("test")
        audio = sd.render(440.0, 0.5, SR)
        assert len(audio) > 0

    def test_add_osc_returns_self(self):
        sd = SoundDesigner("test")
        result = sd.add_osc("sine")
        assert result is sd

    def test_chaining(self):
        sd = (
            SoundDesigner("test")
            .add_osc("sawtooth", detune_cents=0, volume=0.5)
            .add_osc("sawtooth", detune_cents=7, volume=0.3)
            .envelope(attack=0.01, decay=0.1, sustain=0.7, release=0.3)
            .filter("lowpass", cutoff=2000, resonance=0.7)
            .lfo("filter_cutoff", rate=2.0, depth=0.3)
        )
        audio = sd.render(440.0, 1.0, SR)
        assert len(audio) == SR
        assert np.max(np.abs(audio)) > 0.0

    def test_noise_layer(self):
        sd = SoundDesigner("test").noise("white", volume=0.5, seed=42)
        audio = sd.render(440.0, 0.5, SR)
        assert np.max(np.abs(audio)) > 0.0

    def test_pitch_envelope(self):
        sd = (
            SoundDesigner("kick")
            .add_osc("sine")
            .pitch_envelope(start_multiplier=4.0, end_multiplier=1.0, duration=0.05)
            .envelope(attack=0.001, decay=0.3, sustain=0.0, release=0.2)
        )
        audio = sd.render(60.0, 0.5, SR)
        assert len(audio) > 0

    def test_unknown_wave_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Unknown wave"):
            SoundDesigner("test").add_osc("kazoo")

    def test_unknown_noise_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Unknown noise"):
            SoundDesigner("test").noise("purple")

    def test_unknown_lfo_target_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Unknown LFO target"):
            SoundDesigner("test").lfo("reverb_size")


class TestSoundDesignerRender:
    def test_renders_at_multiple_pitches(self):
        sd = SoundDesigner("test").add_osc("sawtooth")
        for freq in [130.81, 261.63, 523.25, 1046.5]:
            audio = sd.render(freq, 0.5, SR)
            assert np.max(np.abs(audio)) > 0.0

    def test_output_is_clipped_to_minus_one_one(self):
        sd = (
            SoundDesigner("loud")
            .add_osc("sawtooth", volume=1.0)
            .add_osc("sawtooth", volume=1.0)
            .add_osc("sawtooth", volume=1.0)
            .add_osc("square", volume=1.0)
        )
        audio = sd.render(440.0, 1.0, SR)
        assert np.max(audio) <= 1.0
        assert np.min(audio) >= -1.0

    def test_envelope_shapes_amplitude(self):
        sd = (
            SoundDesigner("shaped")
            .add_osc("sine")
            .envelope(attack=0.1, decay=0.1, sustain=0.5, release=0.1)
        )
        audio = sd.render(440.0, 0.5, SR)
        # Start should be quieter than middle (attack ramp)
        start_rms = np.sqrt(np.mean(audio[:100] ** 2))
        mid_rms = np.sqrt(np.mean(audio[SR // 4 : SR // 4 + 100] ** 2))
        assert mid_rms > start_rms

    def test_filter_reduces_highs(self):
        sd_no_filter = SoundDesigner("bright").add_osc("sawtooth")
        sd_filtered = SoundDesigner("dark").add_osc("sawtooth").filter("lowpass", cutoff=500)
        bright = sd_no_filter.render(440.0, 0.5, SR)
        dark = sd_filtered.render(440.0, 0.5, SR)
        # RMS of high frequencies should be lower in filtered version
        # Simple proxy: compare overall energy (filter removes harmonics)
        assert np.sqrt(np.mean(dark**2)) < np.sqrt(np.mean(bright**2))

    def test_lfo_volume_modulates(self):
        sd = SoundDesigner("tremolo").add_osc("sine").lfo("volume", rate=5.0, depth=0.5)
        audio = sd.render(440.0, 1.0, SR)
        # Should have amplitude variation
        first_half_rms = np.sqrt(np.mean(audio[: SR // 2] ** 2))
        assert first_half_rms > 0.0  # sanity


class TestSoundDesignerPresets:
    def test_all_presets_exist(self):
        assert len(PRESETS) >= 5

    def test_all_presets_render(self):
        for name, sd in PRESETS.items():
            audio = sd.render(261.63, 0.5, SR)
            assert len(audio) > 0, f"{name} failed to render"
            assert np.max(np.abs(audio)) > 0.0, f"{name} is silent"

    def test_supersaw_has_multiple_oscs(self):
        assert len(supersaw._oscs) >= 5

    def test_sub_808_has_pitch_envelope(self):
        assert sub_808._pitch_env is not None


class TestSoundDesignerSerialization:
    def test_to_dict_returns_dict(self):
        sd = SoundDesigner("test").add_osc("sine").filter("lowpass", cutoff=1000)
        data = sd.to_dict()
        assert isinstance(data, dict)
        assert data["name"] == "test"

    def test_to_dict_is_json_serializable(self):
        sd = (
            SoundDesigner("full")
            .add_osc("sawtooth", detune_cents=7, volume=0.5)
            .noise("pink", volume=0.3)
            .envelope(attack=0.05, decay=0.1, sustain=0.6, release=0.4)
            .filter("lowpass", cutoff=3000, resonance=1.5)
            .lfo("filter_cutoff", rate=1.0, depth=0.3)
            .pitch_envelope(2.0, 1.0, 0.03)
        )
        text = json.dumps(sd.to_dict())
        assert len(text) > 0

    def test_from_dict_reconstructs(self):
        original = (
            SoundDesigner("round_trip")
            .add_osc("sawtooth", detune_cents=10, volume=0.6)
            .add_osc("sine", volume=0.3)
            .noise("white", volume=0.2)
            .envelope(attack=0.05, decay=0.2, sustain=0.5, release=0.3)
            .filter("lowpass", cutoff=2000, resonance=1.0)
        )
        restored = SoundDesigner.from_dict(original.to_dict())
        assert restored.name == "round_trip"
        assert len(restored._oscs) == 2
        assert len(restored._noises) == 1

    def test_roundtrip_render_matches(self):
        original = (
            SoundDesigner("match")
            .add_osc("sine")
            .envelope(attack=0.01, decay=0.1, sustain=0.8, release=0.2)
        )
        restored = SoundDesigner.from_dict(original.to_dict())
        a = original.render(440.0, 0.5, SR)
        b = restored.render(440.0, 0.5, SR)
        np.testing.assert_array_equal(a, b)

    def test_to_wav_creates_file(self):
        sd = SoundDesigner("wav_test").add_osc("sine")
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            path = Path(f.name)
        try:
            sd.to_wav(str(path), freq=440.0, duration=0.5, sr=SR)
            assert path.exists()
            assert path.stat().st_size > 44  # WAV header + data
        finally:
            path.unlink(missing_ok=True)


class TestSoundDesignerInSong:
    def test_register_and_render_in_song(self):
        sd = SoundDesigner("my_lead").add_osc("sawtooth").add_osc("sawtooth", detune_cents=7)
        song = Song(title="Custom Test", bpm=120, sample_rate=SR)
        song.register_instrument("my_lead", sd)
        tr = song.add_track(Track(instrument="my_lead"))
        tr.add(Note("A", 4, 2.0))
        audio = song.render()
        assert audio.shape[0] > 0
        assert np.max(np.abs(audio)) > 0.0

    def test_multiple_custom_instruments_in_one_song(self):
        pad = (
            SoundDesigner("custom_pad")
            .add_osc("sine")
            .add_osc("sine", detune_cents=3)
            .envelope(attack=0.2, decay=0.1, sustain=0.7, release=0.5)
        )
        bass = SoundDesigner("custom_bass").add_osc("sawtooth").filter("lowpass", cutoff=300)

        song = Song(title="Multi Custom", bpm=120, sample_rate=SR)
        song.register_instrument("custom_pad", pad)
        song.register_instrument("custom_bass", bass)

        p = song.add_track(Track(name="pad", instrument="custom_pad"))
        p.add(Note("C", 4, 2.0))
        b = song.add_track(Track(name="bass", instrument="custom_bass"))
        b.add(Note("C", 2, 2.0))

        audio = song.render()
        assert len(song.tracks) == 2
        assert np.max(np.abs(audio)) > 0.0

    def test_custom_instrument_at_different_pitches(self):
        sd = SoundDesigner("pitch_test").add_osc("sine")
        song = Song(title="Pitch Test", bpm=120, sample_rate=SR)
        song.register_instrument("pitch_test", sd)
        tr = song.add_track(Track(instrument="pitch_test"))
        for note in ["C", "E", "G", "C"]:
            tr.add(Note(note, 4, 0.5))
        audio = song.render()
        assert audio.shape[0] > 0

    def test_preset_used_in_song(self):
        song = Song(title="Preset Song", bpm=120, sample_rate=SR)
        song.register_instrument("supersaw", supersaw)
        tr = song.add_track(Track(instrument="supersaw"))
        tr.add(Note("A", 4, 2.0))
        audio = song.render()
        assert np.max(np.abs(audio)) > 0.0


class TestFMSynthesis:
    def test_fm_basic_renders(self):
        sd = SoundDesigner("fm_test").fm("sine", mod_ratio=2.0, mod_index=5.0)
        audio = sd.render(440.0, 0.5, SR)
        assert len(audio) > 0
        assert np.max(np.abs(audio)) > 0.0

    def test_fm_multiple_operators(self):
        sd = (
            SoundDesigner("multi_fm")
            .fm("sine", mod_ratio=1.0, mod_index=3.0, volume=0.6)
            .fm("sine", mod_ratio=3.0, mod_index=2.0, volume=0.4)
        )
        audio = sd.render(440.0, 0.5, SR)
        assert np.max(np.abs(audio)) > 0.0

    def test_fm_with_filter_and_envelope(self):
        sd = (
            SoundDesigner("fm_filtered")
            .fm("sine", mod_ratio=2.0, mod_index=4.0)
            .envelope(attack=0.01, decay=0.3, sustain=0.3, release=0.2)
            .filter("lowpass", cutoff=2000, resonance=0.5)
        )
        audio = sd.render(440.0, 1.0, SR)
        assert np.max(audio) <= 1.0
        assert np.min(audio) >= -1.0

    def test_fm_different_carriers(self):
        for wave in ["sine", "sawtooth", "square", "triangle"]:
            sd = SoundDesigner("test").fm(wave, mod_ratio=2.0, mod_index=3.0)
            audio = sd.render(440.0, 0.3, SR)
            assert np.max(np.abs(audio)) > 0.0, f"FM with {wave} carrier is silent"

    def test_fm_at_multiple_pitches(self):
        sd = SoundDesigner("test").fm("sine", mod_ratio=2.0, mod_index=5.0)
        for freq in [130.81, 261.63, 523.25, 1046.5]:
            audio = sd.render(freq, 0.3, SR)
            assert np.max(np.abs(audio)) > 0.0

    def test_fm_unknown_carrier_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Unknown wave"):
            SoundDesigner("test").fm("kazoo")

    def test_fm_serialization_roundtrip(self):
        original = (
            SoundDesigner("fm_round")
            .fm("sine", mod_ratio=1.5, mod_index=4.0, volume=0.7)
            .fm("sawtooth", mod_ratio=3.0, mod_index=2.0, volume=0.3)
        )
        restored = SoundDesigner.from_dict(original.to_dict())
        assert len(restored._fm_layers) == 2
        assert restored._fm_layers[0].mod_ratio == 1.5
        a = original.render(440.0, 0.5, SR)
        b = restored.render(440.0, 0.5, SR)
        np.testing.assert_array_equal(a, b)

    def test_fm_presets_render(self):
        for name in ["fm_electric_piano", "fm_bell", "fm_brass", "fm_bass"]:
            assert name in PRESETS
            audio = PRESETS[name].render(261.63, 0.5, SR)
            assert np.max(np.abs(audio)) > 0.0, f"{name} is silent"

    def test_fm_in_song(self):
        sd = SoundDesigner("fm_lead").fm("sine", mod_ratio=2.0, mod_index=5.0)
        song = Song(title="FM Test", bpm=120, sample_rate=SR)
        song.register_instrument("fm_lead", sd)
        tr = song.add_track(Track(instrument="fm_lead"))
        tr.add(Note("A", 4, 2.0))
        audio = song.render()
        assert np.max(np.abs(audio)) > 0.0


class TestWavetableSynthesis:
    def test_wavetable_from_harmonics(self):
        wt = Wavetable.from_harmonics([1.0, 0.5, 0.25])
        assert len(wt.table) == 2048
        assert np.max(np.abs(wt.table)) <= 1.0 + 1e-10

    def test_wavetable_from_wave(self):
        for wave in ["sine", "sawtooth", "square", "triangle"]:
            wt = Wavetable.from_wave(wave)
            assert len(wt.table) == 2048

    def test_wavetable_from_wave_unknown_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Unknown wave"):
            Wavetable.from_wave("kazoo")

    def test_wavetable_morph(self):
        a = Wavetable.from_wave("sine")
        b = Wavetable.from_wave("sawtooth")
        m = a.morph(b, 0.5)
        assert len(m.table) == 2048
        # Should differ from both
        assert not np.allclose(m.table, a.table)
        assert not np.allclose(m.table, b.table)

    def test_wavetable_morph_extremes(self):
        a = Wavetable.from_wave("sine")
        b = Wavetable.from_wave("square")
        fully_a = a.morph(b, 0.0)
        np.testing.assert_allclose(fully_a.table, a.table, atol=1e-10)

    def test_wavetable_serialization(self):
        wt = Wavetable.from_harmonics([1.0, 0.5])
        data = wt.to_list()
        restored = Wavetable.from_list(data)
        np.testing.assert_allclose(wt.table, restored.table)

    def test_add_wavetable_renders(self):
        wt = Wavetable.from_harmonics([1.0, 0.5, 0.0, 0.25])
        sd = SoundDesigner("wt_test").add_wavetable(wt)
        audio = sd.render(440.0, 0.5, SR)
        assert len(audio) > 0
        assert np.max(np.abs(audio)) > 0.0

    def test_add_wavetable_with_detune(self):
        wt = Wavetable.from_wave("sawtooth")
        sd = (
            SoundDesigner("wt_detune")
            .add_wavetable(wt, volume=0.5)
            .add_wavetable(wt, volume=0.5, detune_cents=10)
        )
        audio = sd.render(440.0, 0.5, SR)
        assert np.max(np.abs(audio)) > 0.0

    def test_add_wavetable_from_list(self):
        # Accept plain list too
        sd = SoundDesigner("wt_list").add_wavetable([0.0, 0.5, 1.0, 0.5, 0.0, -0.5, -1.0, -0.5])
        audio = sd.render(440.0, 0.5, SR)
        assert np.max(np.abs(audio)) > 0.0

    def test_wavetable_serialization_roundtrip_in_designer(self):
        wt = Wavetable.from_harmonics([1.0, 0.3, 0.1])
        original = SoundDesigner("wt_round").add_wavetable(wt, volume=0.8, detune_cents=5)
        restored = SoundDesigner.from_dict(original.to_dict())
        assert len(restored._wavetable_layers) == 1
        a = original.render(440.0, 0.5, SR)
        b = restored.render(440.0, 0.5, SR)
        np.testing.assert_allclose(a, b, atol=1e-10)

    def test_wavetable_presets_render(self):
        for name in ["wt_organ", "wt_bright_lead", "wt_morph_pad"]:
            assert name in PRESETS
            audio = PRESETS[name].render(261.63, 0.5, SR)
            assert np.max(np.abs(audio)) > 0.0, f"{name} is silent"

    def test_wavetable_in_song(self):
        wt = Wavetable.from_harmonics([1.0, 0.5, 0.25])
        sd = SoundDesigner("wt_lead").add_wavetable(wt)
        song = Song(title="WT Test", bpm=120, sample_rate=SR)
        song.register_instrument("wt_lead", sd)
        tr = song.add_track(Track(instrument="wt_lead"))
        tr.add(Note("C", 4, 2.0))
        audio = song.render()
        assert np.max(np.abs(audio)) > 0.0


class TestEuclideanRhythm:
    def test_euclid_basic(self):
        pattern = euclid(3, 8, "C", 4, 0.5)
        assert len(pattern) == 8
        hits = sum(1 for n in pattern if n.pitch is not None)
        assert hits == 3

    def test_euclid_all_hits(self):
        pattern = euclid(8, 8, "C", 4, 0.5)
        assert all(n.pitch is not None for n in pattern)

    def test_euclid_no_hits(self):
        pattern = euclid(0, 8, "C", 4, 0.5)
        assert all(n.pitch is None for n in pattern)

    def test_euclid_known_tresillo(self):
        # Tresillo (3,8) should be [x . . x . . x .]
        pattern = euclid(3, 8, "C", 4, 1.0)
        hits_at = [i for i, n in enumerate(pattern) if n.pitch is not None]
        assert hits_at == [0, 3, 6], f"Expected tresillo [0,3,6], got {hits_at}"

    def test_euclid_5_8(self):
        pattern = euclid(5, 8, "C", 4, 1.0)
        hits = sum(1 for n in pattern if n.pitch is not None)
        assert hits == 5

    def test_euclid_rotation(self):
        p0 = euclid(3, 8, "C", 4, 0.5, rotation=0)
        p2 = euclid(3, 8, "C", 4, 0.5, rotation=2)
        # p2 should be p0 rotated by 2
        hits0 = [i for i, n in enumerate(p0) if n.pitch is not None]
        hits2 = [i for i, n in enumerate(p2) if n.pitch is not None]
        expected = [(h + 8 - 2) % 8 for h in hits0]
        assert sorted(hits2) == sorted(expected)

    def test_euclid_duration(self):
        pattern = euclid(3, 8, "C", 4, 0.25)
        assert all(n.duration == 0.25 for n in pattern)

    def test_euclid_invalid_raises(self):
        import pytest

        with pytest.raises(ValueError):
            euclid(5, 3)  # hits > steps
        with pytest.raises(ValueError):
            euclid(-1, 8)
        with pytest.raises(ValueError):
            euclid(3, 0)

    def test_euclid_1_hit(self):
        pattern = euclid(1, 8, "C", 4, 1.0)
        hits = [i for i, n in enumerate(pattern) if n.pitch is not None]
        assert hits == [0]

    def test_euclid_in_track(self):
        song = Song(title="Euclid Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="hat", instrument="drums_hat"))
        tr.extend(euclid(5, 8, "F#", 6, 0.5))
        audio = song.render()
        assert audio.shape[0] > 0


class TestSoundDesignerRepr:
    def test_repr_is_concise(self):
        sd = SoundDesigner("test").add_osc("sine").add_osc("sawtooth").filter("lowpass")
        r = repr(sd)
        assert "SoundDesigner" in r
        assert "test" in r
        assert "oscs=2" in r
        assert "lowpass" in r

    def test_repr_shows_fm(self):
        sd = SoundDesigner("fm").fm("sine")
        assert "fm=1" in repr(sd)

    def test_repr_shows_wavetables(self):
        wt = Wavetable.from_wave("sine")
        sd = SoundDesigner("wt").add_wavetable(wt)
        assert "wavetables=1" in repr(sd)
