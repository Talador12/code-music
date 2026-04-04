"""Tests for v66.0 — drone, evolving_pad."""

from code_music.theory import drone, evolving_pad


class TestDrone:
    def test_returns_notes(self):
        notes = drone("C")
        assert len(notes) >= 2  # root + at least 1 overtone

    def test_default_overtones(self):
        notes = drone("C", overtones=4)
        assert len(notes) == 5  # root + 4 overtones

    def test_root_is_first(self):
        notes = drone("A", octave=3)
        assert notes[0].pitch == "A"
        assert notes[0].octave == 3

    def test_overtones_quieter(self):
        notes = drone("C", overtones=3)
        # Each successive overtone should have lower velocity
        for i in range(1, len(notes)):
            assert notes[i].velocity <= notes[i - 1].velocity

    def test_custom_duration(self):
        notes = drone("C", duration=16.0)
        assert all(n.duration == 16.0 for n in notes)


class TestEvolvingPad:
    def test_returns_notes(self):
        notes = evolving_pad("C", seed=42)
        assert len(notes) > 0

    def test_density(self):
        notes = evolving_pad("C", density=5, seed=42)
        assert len(notes) <= 5

    def test_deterministic(self):
        a = evolving_pad("D", seed=99)
        b = evolving_pad("D", seed=99)
        assert [n.pitch for n in a] == [n.pitch for n in b]

    def test_total_duration_bounded(self):
        notes = evolving_pad("C", duration=32.0, seed=42)
        total = sum(n.duration for n in notes)
        assert total <= 32.0 + 0.1  # small float tolerance

    def test_minor_scale(self):
        notes = evolving_pad("A", scale_name="minor", seed=42)
        assert len(notes) > 0
