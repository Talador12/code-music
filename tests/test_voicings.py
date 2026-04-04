"""Tests for v48.0 — rootless_a, rootless_b, quartal_voicing, stride_voicing."""

from code_music.theory import quartal_voicing, rootless_a, rootless_b, stride_voicing


class TestRootlessA:
    def test_dom7_returns_notes(self):
        notes = rootless_a("C", "dom7")
        assert len(notes) >= 3
        # Should NOT contain root C (pitch class 0)
        pitches = [n.pitch for n in notes]
        assert "E" in pitches  # 3rd of C

    def test_maj7(self):
        notes = rootless_a("C", "maj7")
        assert len(notes) >= 3

    def test_min7(self):
        notes = rootless_a("D", "min7")
        assert len(notes) >= 3

    def test_custom_duration(self):
        notes = rootless_a("C", "dom7", duration=2.0)
        assert all(n.duration == 2.0 for n in notes)

    def test_different_keys(self):
        c_notes = rootless_a("C", "dom7")
        g_notes = rootless_a("G", "dom7")
        c_pitches = [n.pitch for n in c_notes]
        g_pitches = [n.pitch for n in g_notes]
        assert c_pitches != g_pitches


class TestRootlessB:
    def test_dom7_returns_notes(self):
        notes = rootless_b("C", "dom7")
        assert len(notes) >= 3

    def test_7th_on_bottom(self):
        notes = rootless_b("C", "dom7")
        # Bb should be lowest (7th of Cdom7)
        assert notes[0].pitch == "Bb"

    def test_maj7(self):
        notes = rootless_b("C", "maj7")
        assert len(notes) >= 3

    def test_min7(self):
        notes = rootless_b("A", "min7")
        assert len(notes) >= 3


class TestQuartalVoicing:
    def test_default_four_layers(self):
        notes = quartal_voicing("C")
        assert len(notes) == 4

    def test_stacked_fourths(self):
        notes = quartal_voicing("C")
        # C, F, Bb, Eb — each a P4 (5 semitones) apart
        pitches = [n.pitch for n in notes]
        assert pitches[0] == "C"
        assert pitches[1] == "F"

    def test_custom_layers(self):
        notes = quartal_voicing("D", layers=6)
        assert len(notes) == 6

    def test_custom_duration(self):
        notes = quartal_voicing("C", duration=2.0)
        assert all(n.duration == 2.0 for n in notes)


class TestStrideVoicing:
    def test_bass_plus_chord(self):
        notes = stride_voicing("C", "maj")
        assert len(notes) >= 4  # root + 3 chord tones

    def test_starts_with_root(self):
        notes = stride_voicing("G", "maj")
        assert notes[0].pitch == "G"

    def test_chord_higher_octave(self):
        notes = stride_voicing("C", "maj", octave=2)
        assert notes[0].octave == 2
        assert notes[1].octave == 3  # chord one octave up

    def test_dom7(self):
        notes = stride_voicing("C", "dom7")
        assert len(notes) == 5  # root + 4 chord tones
