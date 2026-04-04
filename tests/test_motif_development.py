"""Tests for develop_motif() — motif-based composition."""

from code_music.engine import Note
from code_music.theory import develop_motif


class TestDevelopMotif:
    """Motif development produces correct extended passages."""

    def _motif(self):
        return [Note("C", 5, 0.5), Note("D", 5, 0.5), Note("E", 5, 0.5), Note("C", 5, 0.5)]

    def test_basic_repeat(self):
        m = self._motif()
        result = develop_motif(m, techniques=["repeat"], repetitions=1)
        # Original + 1 repeat = 2x motif length
        assert len(result) == len(m) * 2

    def test_sequence_transposes(self):
        m = self._motif()
        result = develop_motif(m, techniques=["sequence"], repetitions=1)
        # Original + sequenced version
        assert len(result) == len(m) * 2
        # Sequenced notes should differ from original
        orig_pitches = [str(n.pitch) for n in result[: len(m)]]
        seq_pitches = [str(n.pitch) for n in result[len(m) :]]
        assert orig_pitches != seq_pitches

    def test_inversion(self):
        m = self._motif()
        result = develop_motif(m, techniques=["inversion"], repetitions=1)
        assert len(result) == len(m) * 2

    def test_retrograde(self):
        m = self._motif()
        result = develop_motif(m, techniques=["retrograde"], repetitions=1)
        # Retrograde reverses
        retro = result[len(m) :]
        assert str(retro[0].pitch) == str(m[-1].pitch)

    def test_augmentation_doubles_duration(self):
        m = self._motif()
        result = develop_motif(m, techniques=["augmentation"], repetitions=1)
        aug_notes = result[len(m) :]
        for orig, aug in zip(m, aug_notes):
            assert abs(aug.duration - orig.duration * 2) < 0.001

    def test_diminution_halves_duration(self):
        m = self._motif()
        result = develop_motif(m, techniques=["diminution"], repetitions=1)
        dim_notes = result[len(m) :]
        for orig, dim in zip(m, dim_notes):
            assert abs(dim.duration - orig.duration / 2) < 0.001

    def test_fragmentation(self):
        m = self._motif()
        result = develop_motif(m, techniques=["fragmentation"], repetitions=1)
        frag_len = len(m) // 2
        # Original + 2x fragment = motif_len + 2*frag_len
        assert len(result) == len(m) + frag_len * 2

    def test_extension_adds_note(self):
        m = self._motif()
        result = develop_motif(m, techniques=["extension"], repetitions=1, seed=42)
        # Extension adds one note to the motif, then appends it
        assert len(result) > len(m) * 2  # at least motif + (motif+1)

    def test_ornamentation(self):
        m = self._motif()
        result = develop_motif(m, techniques=["ornamentation"], repetitions=1, seed=42)
        # Ornamental doubles note count (each note + passing tone)
        assert len(result) > len(m)

    def test_default_arc(self):
        m = self._motif()
        result = develop_motif(m, repetitions=6, seed=42)
        # Default: repeat, sequence, inversion, fragmentation, augmentation, repeat
        assert len(result) > len(m)

    def test_multiple_techniques(self):
        m = self._motif()
        result = develop_motif(m, techniques=["repeat", "sequence", "inversion"], repetitions=3)
        assert len(result) == len(m) * 4  # original + 3 repetitions

    def test_seed_reproducibility(self):
        m = self._motif()
        r1 = develop_motif(m, repetitions=3, seed=42)
        r2 = develop_motif(m, repetitions=3, seed=42)
        assert len(r1) == len(r2)
        p1 = [str(n.pitch) for n in r1]
        p2 = [str(n.pitch) for n in r2]
        assert p1 == p2

    def test_empty_motif(self):
        assert develop_motif([], repetitions=3) == []

    def test_single_note_motif(self):
        m = [Note("C", 5, 1.0)]
        result = develop_motif(m, techniques=["repeat"], repetitions=2)
        assert len(result) == 3  # original + 2 repeats

    def test_invalid_technique_raises(self):
        import pytest

        m = self._motif()
        with pytest.raises(ValueError, match="Unknown technique"):
            develop_motif(m, techniques=["bogus"], repetitions=1)

    def test_retrograde_inversion(self):
        m = self._motif()
        result = develop_motif(m, techniques=["retrograde_inversion"], repetitions=1)
        assert len(result) == len(m) * 2
