"""Tests for v143.0: EnvFollower, sidechain ducking, gating, ModMatrix integration."""

import unittest

import numpy as np

from code_music import EnvFollower, ModMatrix

# ---------------------------------------------------------------------------
# EnvFollower.follow
# ---------------------------------------------------------------------------


class TestEnvFollow(unittest.TestCase):
    """Envelope follower extracts amplitude contour from audio."""

    def test_returns_same_length(self):
        audio = np.random.randn(22050) * 0.3
        env = EnvFollower().follow(audio, 22050)
        assert len(env) == len(audio)

    def test_output_range(self):
        audio = np.random.randn(22050) * 0.5
        env = EnvFollower().follow(audio, 22050)
        assert np.min(env) >= 0.0
        assert np.max(env) <= 1.0 + 1e-6

    def test_stereo_input(self):
        audio = np.random.randn(22050, 2) * 0.3
        env = EnvFollower().follow(audio, 22050)
        assert env.ndim == 1
        assert len(env) == 22050

    def test_silence_produces_zero(self):
        audio = np.zeros(22050)
        env = EnvFollower().follow(audio, 22050)
        assert np.max(env) == 0.0

    def test_loud_burst_detected(self):
        audio = np.zeros(22050)
        # Insert a loud burst at the start
        audio[:500] = 0.9
        env = EnvFollower(attack_ms=1, release_ms=50).follow(audio, 22050)
        # Envelope should peak near the burst
        assert np.argmax(env) < 1000

    def test_attack_affects_rise(self):
        audio = np.zeros(22050)
        audio[1000:1100] = 1.0
        fast = EnvFollower(attack_ms=1).follow(audio, 22050)
        slow = EnvFollower(attack_ms=50).follow(audio, 22050)
        # Fast attack should reach peak sooner
        fast_peak_idx = np.argmax(fast)
        slow_peak_idx = np.argmax(slow)
        assert fast_peak_idx <= slow_peak_idx

    def test_release_affects_decay(self):
        audio = np.zeros(22050)
        audio[:100] = 1.0
        fast = EnvFollower(release_ms=10).follow(audio, 22050)
        slow = EnvFollower(release_ms=500).follow(audio, 22050)
        # At sample 5000, slow release should still have higher value
        assert slow[5000] > fast[5000]


# ---------------------------------------------------------------------------
# EnvFollower.duck (sidechain pump)
# ---------------------------------------------------------------------------


class TestDuck(unittest.TestCase):
    """Sidechain ducking: loud sidechain -> quiet target."""

    def test_duck_reduces_target(self):
        target = np.ones((22050, 2)) * 0.5
        sidechain = np.zeros((22050, 2))
        sidechain[:500] = 0.9  # loud kick hit
        env = EnvFollower(attack_ms=1, release_ms=100)
        ducked = env.duck(target, sidechain, 22050, amount=0.8)
        # During the kick hit, target should be reduced
        assert np.mean(np.abs(ducked[:500])) < np.mean(np.abs(target[:500]))

    def test_duck_amount_zero_is_passthrough(self):
        target = np.random.randn(4410, 2) * 0.3
        sidechain = np.random.randn(4410, 2) * 0.5
        ducked = EnvFollower().duck(target, sidechain, 22050, amount=0.0)
        np.testing.assert_array_almost_equal(ducked, target[:4410])

    def test_duck_mono(self):
        target = np.ones(22050) * 0.5
        sidechain = np.zeros(22050)
        sidechain[:200] = 0.8
        ducked = EnvFollower().duck(target, sidechain, 22050, amount=0.9)
        assert ducked.ndim == 1
        assert len(ducked) == 22050

    def test_duck_shape_preserved(self):
        target = np.random.randn(10000, 2) * 0.3
        sidechain = np.random.randn(10000, 2) * 0.5
        ducked = EnvFollower().duck(target, sidechain, 22050)
        assert ducked.shape == target.shape

    def test_invert_false_gates(self):
        target = np.ones(22050) * 0.5
        sidechain = np.zeros(22050)
        sidechain[:2000] = 0.9  # burst at start
        env = EnvFollower(attack_ms=1, release_ms=50)
        gated = env.duck(target, sidechain, 22050, amount=0.8, invert=False)
        # Where sidechain is quiet (after release), target should be attenuated
        # invert=False means: low envelope -> low gain
        assert np.mean(np.abs(gated[10000:11000])) < np.mean(np.abs(target[10000:11000]))


# ---------------------------------------------------------------------------
# EnvFollower.gate
# ---------------------------------------------------------------------------


class TestGate(unittest.TestCase):
    """Gate target audio based on sidechain envelope level."""

    def test_gate_silences_below_threshold(self):
        target = np.ones(22050) * 0.5
        sidechain = np.zeros(22050)
        sidechain[:500] = 0.9  # only loud at start
        gated = EnvFollower(release_ms=10).gate(
            target, sidechain, 22050, threshold=0.3, amount=0.95
        )
        # Well after the burst, target should be nearly silent
        assert np.mean(np.abs(gated[5000:6000])) < 0.15

    def test_gate_passes_above_threshold(self):
        target = np.ones(22050) * 0.5
        sidechain = np.ones(22050) * 0.8  # always loud
        gated = EnvFollower().gate(target, sidechain, 22050, threshold=0.3, amount=0.9)
        # Sidechain is always loud, so target should pass through
        assert np.mean(np.abs(gated)) > 0.3

    def test_gate_shape_preserved(self):
        target = np.random.randn(5000, 2) * 0.3
        sidechain = np.random.randn(5000, 2) * 0.5
        gated = EnvFollower().gate(target, sidechain, 22050)
        assert gated.shape == target.shape


# ---------------------------------------------------------------------------
# ModMatrix integration
# ---------------------------------------------------------------------------


class TestModMatrixEnvFollower(unittest.TestCase):
    """ModMatrix.connect_env_follower wires sidechain to destinations."""

    def test_connect_env_follower(self):
        mm = ModMatrix()
        kick = np.random.randn(22050) * 0.5
        mm.connect_env_follower("pad.volume", kick, amount=-0.8)
        assert mm.env_follower_count == 1
        assert len(mm) == 1

    def test_generate_env_follower_signals(self):
        mm = ModMatrix()
        kick = np.zeros(22050)
        kick[:500] = 0.9
        mm.connect_env_follower("pad.volume", kick, amount=-0.8)
        signals = mm.generate_env_follower_signals(22050, 22050)
        assert len(signals) == 1
        dest, amount, env = signals[0]
        assert dest == "pad.volume"
        assert amount == -0.8
        assert len(env) == 22050

    def test_multiple_followers(self):
        mm = ModMatrix()
        mm.connect_env_follower("pad.volume", np.zeros(1000), amount=-0.8)
        mm.connect_env_follower("bass.volume", np.zeros(1000), amount=-0.5)
        assert mm.env_follower_count == 2
        assert len(mm) == 2

    def test_combined_routes_and_followers(self):
        mm = ModMatrix()
        mm.connect("lfo1", "pad.volume", amount=0.3, rate=2.0)
        mm.connect_env_follower("bass.volume", np.zeros(1000), amount=-0.5)
        assert len(mm) == 2
        assert mm.env_follower_count == 1

    def test_import_from_top_level(self):
        from code_music import EnvFollower

        assert callable(EnvFollower)


if __name__ == "__main__":
    unittest.main()
