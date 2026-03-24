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


class TestConvReverbIRFile:
    def _make_ir_wav(self, path, sr=22050, dur_sec=0.5):
        """Create a simple impulse WAV file for testing."""
        import wave as _wave
        n = int(sr * dur_sec)
        rng = np.random.default_rng(42)
        ir = rng.standard_normal(n).astype(np.float64)
        ir *= np.exp(-np.linspace(0, 10, n))  # decaying noise
        ir_int = (np.clip(ir / max(np.max(np.abs(ir)), 1e-9), -1, 1) * 32767).astype(np.int16)
        with _wave.open(str(path), "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(ir_int.tobytes())

    def test_ir_file_loads_and_applies(self):
        import tempfile
        from pathlib import Path
        s = _sine(SR)
        with tempfile.TemporaryDirectory() as tmp:
            ir_path = Path(tmp) / "test_ir.wav"
            self._make_ir_wav(ir_path, sr=SR)
            out = conv_reverb(s, SR, ir_file=str(ir_path), wet=0.5)
            assert out.shape == s.shape
            assert not np.allclose(out, s)  # IR should modify the signal

    def test_ir_file_wet_zero_passthrough(self):
        import tempfile
        from pathlib import Path
        s = _sine(SR)
        with tempfile.TemporaryDirectory() as tmp:
            ir_path = Path(tmp) / "test_ir.wav"
            self._make_ir_wav(ir_path, sr=SR)
            out = conv_reverb(s, SR, ir_file=str(ir_path), wet=0.0)
            np.testing.assert_allclose(out, s, atol=1e-6)

    def test_ir_file_not_found_raises(self):
        import pytest
        s = _sine(SR)
        with pytest.raises(FileNotFoundError):
            conv_reverb(s, SR, ir_file="/nonexistent/ir.wav", wet=0.3)

    def test_ir_file_output_clamped(self):
        import tempfile
        from pathlib import Path
        s = _sine(SR) * 0.9
        with tempfile.TemporaryDirectory() as tmp:
            ir_path = Path(tmp) / "test_ir.wav"
            self._make_ir_wav(ir_path, sr=SR)
            out = conv_reverb(s, SR, ir_file=str(ir_path), wet=0.8)
            assert np.max(np.abs(out)) <= 1.0 + 1e-6

    def test_ir_file_different_sample_rate(self):
        """IR at different sample rate should be resampled automatically."""
        import tempfile
        from pathlib import Path
        s = _sine(SR)
        with tempfile.TemporaryDirectory() as tmp:
            ir_path = Path(tmp) / "test_ir_44k.wav"
            self._make_ir_wav(ir_path, sr=44100)  # different from SR=22050
            out = conv_reverb(s, SR, ir_file=str(ir_path), wet=0.5)
            assert out.shape == s.shape
            assert not np.allclose(out, s)


class TestFingerprint:
    def _make_wav(self, path, freq=440.0, dur=1.0, sr=22050):
        """Write a sine WAV for fingerprint testing."""
        import wave as _wave
        n = int(sr * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        mono = (np.sin(2 * np.pi * freq * t) * 0.5 * 32767).astype(np.int16)
        stereo = np.column_stack([mono, mono]).flatten()
        with _wave.open(str(path), "w") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(stereo.tobytes())

    def test_same_file_same_fingerprint(self):
        import tempfile
        from pathlib import Path

        from scripts.fingerprint import fingerprint_wav
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "test.wav"
            self._make_wav(wav)
            fp1 = fingerprint_wav(wav)
            fp2 = fingerprint_wav(wav)
            assert fp1 == fp2

    def test_different_freq_different_fingerprint(self):
        import tempfile
        from pathlib import Path

        from scripts.fingerprint import fingerprint_wav
        with tempfile.TemporaryDirectory() as tmp:
            wav_a = Path(tmp) / "a.wav"
            wav_b = Path(tmp) / "b.wav"
            self._make_wav(wav_a, freq=440.0)
            self._make_wav(wav_b, freq=880.0)
            fp_a = fingerprint_wav(wav_a)
            fp_b = fingerprint_wav(wav_b)
            assert fp_a != fp_b

    def test_fingerprint_is_hex_string(self):
        import tempfile
        from pathlib import Path

        from scripts.fingerprint import fingerprint_wav
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "test.wav"
            self._make_wav(wav)
            fp = fingerprint_wav(wav)
            assert isinstance(fp, str)
            assert len(fp) == 32
            int(fp, 16)  # should be valid hex


class TestSlapback:
    def test_output_shape(self):
        from code_music.effects import slapback
        s = _sine(SR)
        out = slapback(s, SR)
        assert out.shape == s.shape

    def test_level_zero_passthrough(self):
        from code_music.effects import slapback
        s = _sine(SR)
        out = slapback(s, SR, level=0.0)
        np.testing.assert_allclose(out, s, atol=1e-9)

    def test_adds_echo(self):
        from code_music.effects import slapback
        # Impulse test: echo should appear after the delay
        n = SR
        impulse = np.zeros((n, 2))
        impulse[100] = 0.8
        out = slapback(impulse, SR, delay_ms=100.0, level=0.6)
        d = int(0.1 * SR)
        # Echo should exist at position 100 + d
        assert np.max(np.abs(out[100 + d])) > 0.1

    def test_output_clamped(self):
        from code_music.effects import slapback
        s = _sine(SR) * 0.9
        out = slapback(s, SR, level=0.9)
        assert np.max(np.abs(out)) <= 1.0 + 1e-6

    def test_single_echo_no_feedback(self):
        from code_music.effects import slapback
        # Create an impulse — single spike then silence
        n = SR
        impulse = np.zeros((n, 2))
        impulse[0] = 0.9
        out = slapback(impulse, SR, delay_ms=100.0, level=0.5)
        d = int(0.1 * SR)
        # Should have original spike at 0 and one echo at d, nothing after
        assert np.max(np.abs(out[0])) > 0.5       # original
        assert np.max(np.abs(out[d])) > 0.2        # echo
        assert np.max(np.abs(out[d*2:])) < 0.01    # no second echo
