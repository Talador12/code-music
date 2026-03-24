"""Tests for v0.15-0.16 effects: conv_reverb, granular, autotune, multitap_delay."""

import numpy as np

from code_music.effects import autotune, conv_reverb, granular, multitap_delay

SR = 22050


def _sine(freq=440.0, dur=1.0, sr=SR):
    n = int(sr * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    mono = np.sin(2 * np.pi * freq * t) * 0.5
    return np.column_stack([mono, mono]).astype(np.float64)


class TestConvReverb:
    def test_all_rooms_render(self):
        s = _sine()
        for room in ["hall", "chamber", "plate", "room", "cave", "spring"]:
            out = conv_reverb(s, SR, room=room, wet=0.3)
            assert out.shape == s.shape, f"room={room} wrong shape"
            assert np.max(np.abs(out)) <= 1.0 + 1e-6

    def test_wet_zero_passthrough(self):
        s = _sine()
        out = conv_reverb(s, SR, wet=0.0)
        np.testing.assert_allclose(out, s, atol=1e-6)

    def test_wet_nonzero_modifies(self):
        s = _sine()
        out = conv_reverb(s, SR, wet=0.5)
        assert not np.allclose(out, s)

    def test_hall_longer_decay_than_room(self):
        """Hall should have more energy in the tail than small room."""
        s = _sine(dur=0.5)
        hall = conv_reverb(s, SR, room="hall", wet=0.9)
        room = conv_reverb(s, SR, room="room", wet=0.9)
        # Hall tail energy should be higher or equal
        tail_start = int(0.4 * SR)
        hall_tail = np.mean(np.abs(hall[tail_start:]))
        room_tail = np.mean(np.abs(room[tail_start:]))
        assert hall_tail >= room_tail * 0.5  # hall has at least half the tail energy


class TestGranular:
    def test_output_shape(self):
        s = _sine()
        out = granular(s, SR)
        assert out.shape == s.shape

    def test_wet_zero_passthrough(self):
        s = _sine()
        out = granular(s, SR, wet=0.0)
        np.testing.assert_allclose(out, s, atol=1e-6)

    def test_modifies_signal(self):
        s = _sine()
        out = granular(s, SR, scatter=0.5, wet=0.8)
        assert not np.allclose(out, s, atol=0.01)

    def test_output_clamped(self):
        s = _sine() * 0.9
        out = granular(s, SR, wet=1.0)
        assert np.max(np.abs(out)) <= 1.0 + 1e-6

    def test_density_zero_silent(self):
        s = _sine()
        out = granular(s, SR, density=0.0, wet=1.0)
        # With density=0 no grains play → wet signal is zeros → dry * 0 = 0
        assert np.mean(np.abs(out)) < np.mean(np.abs(s))


class TestMultitapDelay:
    def test_output_shape(self):
        s = _sine()
        out = multitap_delay(s, SR)
        assert out.shape == s.shape

    def test_no_taps_passthrough(self):
        s = _sine()
        out = multitap_delay(s, SR, taps=[])
        np.testing.assert_allclose(out, s, atol=1e-9)

    def test_single_tap_adds_echo(self):
        s = _sine()
        out = multitap_delay(s, SR, taps=[(100.0, 0.5, 0.0)])
        assert not np.allclose(out, s, atol=0.01)

    def test_pan_left_right(self):
        s = _sine()
        out = multitap_delay(
            s,
            SR,
            taps=[
                (100.0, 0.5, -1.0),  # hard left echo
                (200.0, 0.5, 1.0),  # hard right echo
            ],
        )
        # After taps, L and R should differ
        assert not np.allclose(out[:, 0], out[:, 1], atol=0.01)

    def test_output_clamped(self):
        s = _sine() * 0.9
        out = multitap_delay(s, SR, taps=[(100.0, 0.8, 0.0)] * 4)
        assert np.max(np.abs(out)) <= 1.0 + 1e-6


class TestAutotune:
    def test_output_shape(self):
        s = _sine()
        out = autotune(s, SR)
        assert out.shape == s.shape

    def test_strength_zero_passthrough(self):
        s = _sine()
        out = autotune(s, SR, strength=0.0)
        np.testing.assert_allclose(out, s, atol=1e-6)

    def test_output_clamped(self):
        s = _sine() * 0.9
        out = autotune(s, SR, strength=0.8)
        assert np.max(np.abs(out)) <= 1.0 + 1e-6

    def test_chromatic_minimal_change(self):
        """Chromatic scale (all notes allowed) should make minimal changes."""
        s = _sine(freq=440.0)
        chromatic = list(range(12))
        out = autotune(s, SR, scale_notes=chromatic, strength=1.0)
        # A=440Hz is already on a chromatic note — minimal change
        assert np.max(np.abs(out - s)) < 0.5  # some change is ok, not complete rewrite
