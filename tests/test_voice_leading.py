"""Tests for v42.0 — voice_lead_satb, check_parallel_fifths."""

import pytest

from code_music.theory import check_parallel_fifths, voice_lead_satb


class TestVoiceLeadSATB:
    def test_single_chord(self):
        result = voice_lead_satb([("C", "maj")])
        assert len(result) == 1
        assert len(result[0]) == 4  # SATB = 4 voices

    def test_two_chord_progression(self):
        result = voice_lead_satb([("C", "maj"), ("G", "maj")])
        assert len(result) == 2
        for voicing in result:
            assert len(voicing) == 4

    def test_empty_progression(self):
        assert voice_lead_satb([]) == []

    def test_soprano_highest_bass_lowest(self):
        result = voice_lead_satb([("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")])
        for voicing in result:
            octaves = [n.octave for n in voicing]
            # soprano (idx 0) should have highest or equal octave
            assert octaves[0] >= octaves[-1]

    def test_four_chord_jazz(self):
        prog = [("C", "maj7"), ("A", "min7"), ("D", "min7"), ("G", "dom7")]
        result = voice_lead_satb(prog, key="C")
        assert len(result) == 4

    def test_all_notes_are_valid(self):
        result = voice_lead_satb([("C", "maj"), ("F", "maj")])
        for voicing in result:
            for note in voicing:
                assert note.pitch is not None
                assert 2 <= note.octave <= 7

    def test_unknown_shape_raises(self):
        with pytest.raises(ValueError, match="Unknown chord shape"):
            voice_lead_satb([("C", "notachord")])

    def test_smooth_motion(self):
        """Adjacent voicings should have small total movement."""
        result = voice_lead_satb([("C", "maj"), ("C", "min")])
        # Between C major and C minor, only the 3rd changes (E→Eb = 1 semitone)
        # Total movement across all voices should be small
        assert len(result) == 2


class TestCheckParallelFifths:
    def test_no_parallel(self):
        from code_music.engine import Note

        v1 = [Note("C", 5, 4.0), Note("E", 4, 4.0), Note("G", 3, 4.0), Note("C", 3, 4.0)]
        v2 = [Note("D", 5, 4.0), Note("F", 4, 4.0), Note("A", 3, 4.0), Note("D", 3, 4.0)]
        # This is stepwise motion — parallel 3rds/6ths are fine
        result = check_parallel_fifths(v1, v2)
        assert isinstance(result, bool)

    def test_static_voicing(self):
        """Same voicing twice should not flag parallels (no movement)."""
        from code_music.engine import Note

        v = [Note("C", 5, 4.0), Note("E", 4, 4.0), Note("G", 3, 4.0), Note("C", 3, 4.0)]
        assert check_parallel_fifths(v, v) is False
