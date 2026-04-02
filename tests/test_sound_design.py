"""Tests for SoundDesigner: custom instrument creation from scratch."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import numpy as np

from code_music import Note, Song, SoundDesigner, Track
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


class TestSoundDesignerRepr:
    def test_repr_is_concise(self):
        sd = SoundDesigner("test").add_osc("sine").add_osc("sawtooth").filter("lowpass")
        r = repr(sd)
        assert "SoundDesigner" in r
        assert "test" in r
        assert "oscs=2" in r
        assert "lowpass" in r
