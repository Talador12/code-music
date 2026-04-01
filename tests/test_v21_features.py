"""Tests for v2.1 features: Track.transpose, Track.loop, Song.render, EffectsChain serialization."""

from __future__ import annotations

import numpy as np

from code_music.effects import EffectsChain, delay, reverb
from code_music.engine import Chord, Note, Song, Track


class TestTrackTranspose:
    def test_transpose_up_shifts_pitch(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 1.0))
        up = t.transpose(4)
        assert up.beats[0].event.pitch == "E"
        assert up.beats[0].event.octave == 4

    def test_transpose_down_shifts_pitch(self):
        t = Track(instrument="piano")
        t.add(Note("E", 4, 1.0))
        down = t.transpose(-4)
        assert down.beats[0].event.pitch == "C"
        assert down.beats[0].event.octave == 4

    def test_transpose_crosses_octave_boundary(self):
        t = Track(instrument="piano")
        t.add(Note("A", 4, 1.0))
        up = t.transpose(5)
        assert up.beats[0].event.pitch == "D"
        assert up.beats[0].event.octave == 5

    def test_transpose_preserves_rests(self):
        t = Track(instrument="piano")
        t.add(Note.rest(2.0))
        up = t.transpose(7)
        assert up.beats[0].event.pitch is None

    def test_transpose_preserves_velocity(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 1.0, velocity=0.3))
        up = t.transpose(2)
        assert up.beats[0].event.velocity == 0.3

    def test_transpose_preserves_duration(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 2.5))
        up = t.transpose(1)
        assert up.beats[0].event.duration == 2.5

    def test_transpose_preserves_metadata(self):
        t = Track(name="lead", instrument="sawtooth", volume=0.7, pan=0.2)
        t.add(Note("C", 4, 1.0))
        up = t.transpose(5)
        assert up.name == "lead"
        assert up.instrument == "sawtooth"
        assert up.volume == 0.7

    def test_transpose_handles_chords(self):
        t = Track(instrument="piano")
        t.add(Chord("C", "min", 3, duration=4.0))
        up = t.transpose(3)
        assert up.beats[0].event.root == "D#"
        assert up.beats[0].event.shape == "min"

    def test_transpose_does_not_mutate_original(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 1.0))
        _ = t.transpose(5)
        assert t.beats[0].event.pitch == "C"

    def test_transpose_by_octave(self):
        t = Track(instrument="piano")
        t.add(Note("A", 4, 1.0))
        up = t.transpose(12)
        assert up.beats[0].event.pitch == "A"
        assert up.beats[0].event.octave == 5


class TestTrackLoop:
    def test_loop_doubles_beats(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 1.0))
        t.add(Note("E", 4, 1.0))
        looped = t.loop(2)
        assert len(looped.beats) == 4

    def test_loop_total_beats_is_multiple(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 2.0))
        looped = t.loop(3)
        assert looped.total_beats == 6.0

    def test_loop_preserves_metadata(self):
        t = Track(name="bass", instrument="bass", volume=0.6, pan=-0.1)
        t.add(Note("E", 2, 1.0))
        looped = t.loop(4)
        assert looped.name == "bass"
        assert looped.instrument == "bass"
        assert looped.volume == 0.6

    def test_loop_does_not_mutate_original(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 1.0))
        _ = t.loop(5)
        assert len(t.beats) == 1

    def test_loop_one_is_identity_length(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 1.0))
        looped = t.loop(1)
        assert len(looped.beats) == 1

    def test_loop_chains_with_transpose(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 1.0))
        result = t.loop(2).transpose(7)
        assert len(result.beats) == 2
        assert result.beats[0].event.pitch == "G"


class TestSongRender:
    def test_render_returns_stereo_array(self):
        song = Song(title="Render Test", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(instrument="sine"))
        tr.add(Note("A", 4, 1.0))
        audio = song.render()
        assert audio.ndim == 2
        assert audio.shape[1] == 2

    def test_render_produces_non_silent_audio(self):
        song = Song(title="Render Test", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(instrument="sine"))
        tr.add(Note("A", 4, 1.0))
        audio = song.render()
        assert np.max(np.abs(audio)) > 0.0

    def test_render_matches_explicit_synth_call(self):
        from code_music.synth import Synth

        song = Song(title="Match Test", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(instrument="sine"))
        tr.add(Note("C", 4, 2.0))

        via_render = song.render()
        via_synth = Synth(22050).render_song(song)
        np.testing.assert_array_equal(via_render, via_synth)

    def test_render_respects_sample_rate(self):
        song = Song(title="SR Test", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(instrument="sine"))
        tr.add(Note("C", 4, 1.0))
        audio = song.render()
        # 1 beat at 120 BPM = 0.5s → ~11025 samples + padding
        assert audio.shape[0] < 22050 * 2


SR = 22050


def _make_signal(seconds: float = 0.5) -> np.ndarray:
    t = np.linspace(0, seconds, int(SR * seconds), endpoint=False)
    mono = np.sin(2 * np.pi * 440 * t) * 0.5
    return np.column_stack([mono, mono])


class TestEffectsChainSerialization:
    def test_to_dict_single_effect(self):
        chain = EffectsChain().add(reverb, room_size=0.7, wet=0.3, label="reverb")
        data = chain.to_dict()
        assert len(data) == 1
        assert data[0]["effect"] == "reverb"
        assert data[0]["wet"] == 0.3
        assert data[0]["room_size"] == 0.7

    def test_to_dict_multiple_effects(self):
        chain = (
            EffectsChain()
            .add(reverb, room_size=0.5, wet=0.2, label="reverb")
            .add(delay, delay_ms=375, wet=0.25, label="delay")
        )
        data = chain.to_dict()
        assert len(data) == 2
        assert data[0]["effect"] == "reverb"
        assert data[1]["effect"] == "delay"
        assert data[1]["delay_ms"] == 375

    def test_to_dict_preserves_bypass(self):
        chain = EffectsChain().add(reverb, room_size=0.5, bypass=True, label="reverb")
        data = chain.to_dict()
        assert data[0]["bypass"] is True

    def test_from_dict_reconstructs_chain(self):
        data = [
            {"effect": "reverb", "wet": 0.3, "room_size": 0.7},
            {"effect": "delay", "wet": 0.2, "delay_ms": 200},
        ]
        chain = EffectsChain.from_dict(data)
        assert len(chain) == 2

    def test_from_dict_produces_working_chain(self):
        data = [{"effect": "reverb", "wet": 0.3, "room_size": 0.5}]
        chain = EffectsChain.from_dict(data)
        sig = _make_signal()
        result = chain(sig, SR)
        assert not np.array_equal(result, sig)

    def test_roundtrip_to_dict_from_dict(self):
        original = (
            EffectsChain()
            .add(reverb, room_size=0.7, wet=0.3, label="reverb")
            .add(delay, delay_ms=375, feedback=0.3, wet=0.25, label="delay")
        )
        data = original.to_dict()
        restored = EffectsChain.from_dict(data)

        sig = _make_signal()
        result_orig = original(sig.copy(), SR)
        result_rest = restored(sig.copy(), SR)
        np.testing.assert_allclose(result_orig, result_rest, atol=1e-6)

    def test_from_dict_raises_on_unknown_effect(self):
        import pytest

        with pytest.raises(ValueError, match="Unknown effect"):
            EffectsChain.from_dict([{"effect": "nonexistent_fx"}])
