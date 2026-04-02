"""Tests for Automation, ModMatrix, and song composition utilities."""

from __future__ import annotations

import numpy as np
import pytest

from code_music import Note, Song, Track
from code_music.automation import (
    Automation,
    ModMatrix,
    song_append,
    song_extract,
    song_overlay,
)

SR = 22050


class TestAutomation:
    def test_single_keyframe(self):
        a = Automation([(0, 0.5)])
        assert a.value_at(0) == 0.5
        assert a.value_at(10) == 0.5

    def test_two_keyframes_linear(self):
        a = Automation([(0, 0.0), (10, 1.0)])
        assert a.value_at(0) == 0.0
        assert abs(a.value_at(5) - 0.5) < 0.01
        assert a.value_at(10) == 1.0

    def test_before_first_keyframe(self):
        a = Automation([(4, 0.5), (8, 1.0)])
        assert a.value_at(0) == 0.5

    def test_after_last_keyframe(self):
        a = Automation([(0, 0.0), (4, 1.0)])
        assert a.value_at(100) == 1.0

    def test_three_keyframes(self):
        a = Automation([(0, 0.0), (4, 0.8), (12, 0.3)])
        assert a.value_at(0) == 0.0
        assert abs(a.value_at(4) - 0.8) < 0.01
        assert abs(a.value_at(12) - 0.3) < 0.01

    def test_smoothstep_mode(self):
        a = Automation([(0, 0.0), (10, 1.0)], mode="smoothstep")
        mid = a.value_at(5)
        assert 0.0 < mid < 1.0
        # Smoothstep midpoint should be 0.5
        assert abs(mid - 0.5) < 0.01

    def test_exponential_mode(self):
        a = Automation([(0, 0.1), (10, 1.0)], mode="exponential")
        assert a.value_at(0) == pytest.approx(0.1, abs=0.01)
        assert a.value_at(10) == pytest.approx(1.0, abs=0.01)

    def test_sample(self):
        a = Automation([(0, 0.0), (4, 1.0)])
        values = a.sample(bpm=120, sr=SR, duration_beats=4)
        assert len(values) > 0
        assert values[0] == pytest.approx(0.0, abs=0.01)
        assert values[-1] == pytest.approx(1.0, abs=0.02)

    def test_sample_empty_duration(self):
        a = Automation([(0, 0.5)])
        values = a.sample(bpm=120, sr=SR, duration_beats=0)
        assert len(values) == 0

    def test_empty_keyframes_raises(self):
        with pytest.raises(ValueError, match="at least one keyframe"):
            Automation([])

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError, match="Unknown mode"):
            Automation([(0, 0.0)], mode="cubic")

    def test_unsorted_keyframes(self):
        a = Automation([(8, 1.0), (0, 0.0), (4, 0.5)])
        assert a.keyframes[0][0] == 0
        assert a.value_at(4) == pytest.approx(0.5, abs=0.01)

    def test_repr(self):
        a = Automation([(0, 0.0), (4, 1.0)])
        r = repr(a)
        assert "Automation" in r
        assert "2 keyframes" in r


class TestModMatrix:
    def test_connect(self):
        mm = ModMatrix()
        mm.connect("lfo1", "pad.volume", amount=0.3, rate=2.0)
        assert len(mm) == 1

    def test_multiple_routes(self):
        mm = ModMatrix()
        mm.connect("lfo1", "pad.volume", amount=0.3)
        mm.connect("random", "lead.pan", amount=0.2)
        assert len(mm) == 2

    def test_routes_property(self):
        mm = ModMatrix()
        mm.connect("lfo1", "pad.volume", amount=0.3, rate=2.0)
        routes = mm.routes
        assert routes[0]["source"] == "lfo1"
        assert routes[0]["dest"] == "pad.volume"
        assert routes[0]["amount"] == 0.3

    def test_generate_lfo_signal(self):
        mm = ModMatrix()
        signal = mm.generate_mod_signal("lfo1", SR, SR, rate=1.0)
        assert len(signal) == SR
        assert np.max(signal) <= 1.0
        assert np.min(signal) >= -1.0

    def test_generate_random_signal(self):
        mm = ModMatrix()
        signal = mm.generate_mod_signal("random", SR, SR, rate=1.0, seed=42)
        assert len(signal) == SR
        assert np.max(np.abs(signal)) > 0.0

    def test_generate_envelope_signal(self):
        mm = ModMatrix()
        signal = mm.generate_mod_signal("envelope", SR, SR)
        assert signal[0] < signal[SR // 2]  # attack phase
        assert signal[-1] < signal[SR // 2]  # release phase

    def test_generate_unknown_source(self):
        mm = ModMatrix()
        signal = mm.generate_mod_signal("unknown", SR, SR)
        assert np.allclose(signal, 0.0)

    def test_chaining(self):
        mm = ModMatrix().connect("lfo1", "a.b").connect("lfo2", "c.d")
        assert len(mm) == 2

    def test_repr(self):
        mm = ModMatrix()
        mm.connect("lfo1", "pad.volume")
        assert "ModMatrix(1 routes)" in repr(mm)


class TestSongOverlay:
    def test_overlay_adds_tracks(self):
        base = Song(title="Base", bpm=120, sample_rate=SR)
        base.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))

        other = Song(title="Other", bpm=120, sample_rate=SR)
        tr = Track(name="pad", instrument="pad", volume=0.4)
        tr.add(Note("C", 4, 4.0))
        other.add_track(tr)

        song_overlay(base, other)
        assert len(base.tracks) == 2
        assert base.tracks[1].name == "pad"

    def test_overlay_name_collision(self):
        base = Song(title="Base", bpm=120, sample_rate=SR)
        base.add_track(Track(name="pad", instrument="pad"))

        other = Song(title="Other", bpm=120, sample_rate=SR)
        other.add_track(Track(name="pad", instrument="pad"))

        song_overlay(base, other)
        names = [t.name for t in base.tracks]
        assert "pad" in names
        assert "pad_2" in names


class TestSongAppend:
    def test_append_creates_new_song(self):
        a = Song(title="A", bpm=120, sample_rate=SR)
        tr_a = a.add_track(Track(name="lead", instrument="piano"))
        tr_a.add(Note("C", 4, 4.0))

        b = Song(title="B", bpm=120, sample_rate=SR)
        tr_b = b.add_track(Track(name="bass", instrument="bass"))
        tr_b.add(Note("C", 2, 4.0))

        combined = song_append(a, b)
        assert "A + B" in combined.title
        assert len(combined.tracks) == 2

    def test_append_same_track_name(self):
        a = Song(title="A", bpm=120, sample_rate=SR)
        tr_a = a.add_track(Track(name="lead", instrument="piano"))
        tr_a.add(Note("C", 4, 4.0))

        b = Song(title="B", bpm=120, sample_rate=SR)
        tr_b = b.add_track(Track(name="lead", instrument="piano"))
        tr_b.add(Note("E", 4, 4.0))

        combined = song_append(a, b)
        # Same name should concatenate beats
        lead_tracks = [t for t in combined.tracks if t.name == "lead"]
        assert len(lead_tracks) == 1
        assert len(lead_tracks[0].beats) == 2  # both notes


class TestSongExtract:
    def test_extract_specific_tracks(self):
        song = Song(title="Full", bpm=120, sample_rate=SR)
        song.add_track(Track(name="kick", instrument="drums_kick"))
        song.add_track(Track(name="pad", instrument="pad"))
        song.add_track(Track(name="lead", instrument="piano"))

        extracted = song_extract(song, ["kick", "lead"])
        assert len(extracted.tracks) == 2
        names = [t.name for t in extracted.tracks]
        assert "kick" in names
        assert "lead" in names
        assert "pad" not in names

    def test_extract_preserves_effects(self):
        from code_music import EffectsChain, reverb

        song = Song(title="Full", bpm=120, sample_rate=SR)
        song.add_track(Track(name="pad", instrument="pad"))
        song.add_track(Track(name="lead", instrument="piano"))
        song.effects = {
            "pad": EffectsChain().add(reverb, room_size=0.5, wet=0.3),
            "lead": EffectsChain().add(reverb, room_size=0.3, wet=0.2),
        }

        extracted = song_extract(song, ["pad"])
        assert "pad" in extracted.effects
        assert "lead" not in extracted.effects

    def test_extract_renders(self):
        song = Song(title="Full", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano", volume=0.5))
        tr.add(Note("C", 4, 2.0))

        extracted = song_extract(song, ["lead"])
        audio = extracted.render()
        assert np.max(np.abs(audio)) > 0.0
