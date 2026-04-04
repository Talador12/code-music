"""Tests for v59.0 — groove_template, apply_groove, extract_groove."""

import pytest

from code_music.engine import Note
from code_music.theory import apply_groove, extract_groove, groove_template


class TestGrooveTemplate:
    def test_straight(self):
        t = groove_template("straight")
        assert len(t) == 16
        assert all(v == 0.0 for v in t)

    def test_mpc_swing(self):
        t = groove_template("mpc_swing")
        assert len(t) == 16
        assert any(v != 0.0 for v in t)

    def test_j_dilla(self):
        t = groove_template("j_dilla")
        assert len(t) == 16

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown groove"):
            groove_template("nonexistent")

    def test_all_grooves(self):
        for name in ["straight", "mpc_swing", "j_dilla", "motown", "shuffle", "bossa"]:
            t = groove_template(name)
            assert len(t) == 16


class TestApplyGroove:
    def test_straight_no_change(self):
        notes = [Note("C", 5, 0.25) for _ in range(4)]
        result = apply_groove(notes, groove_template("straight"))
        assert all(abs(n.duration - 0.25) < 1e-9 for n in result)

    def test_groove_changes_duration(self):
        notes = [Note("C", 5, 0.25) for _ in range(16)]
        t = groove_template("j_dilla")
        result = apply_groove(notes, t)
        # At least some durations should differ from 0.25
        assert any(abs(n.duration - 0.25) > 0.001 for n in result)

    def test_strength_zero(self):
        notes = [Note("C", 5, 0.25) for _ in range(4)]
        result = apply_groove(notes, groove_template("j_dilla"), strength=0.0)
        assert all(abs(n.duration - 0.25) < 1e-9 for n in result)

    def test_empty_notes(self):
        assert apply_groove([], groove_template("straight")) == []

    def test_preserves_pitch(self):
        notes = [Note("E", 4, 0.25)]
        result = apply_groove(notes, groove_template("mpc_swing"))
        assert result[0].pitch == "E"


class TestExtractGroove:
    def test_on_grid(self):
        notes = [Note("C", 5, 0.25) for _ in range(4)]
        offsets = extract_groove(notes, grid_duration=0.25)
        assert all(abs(o) < 1e-9 for o in offsets)

    def test_off_grid(self):
        notes = [Note("C", 5, 0.30), Note("C", 5, 0.20)]
        offsets = extract_groove(notes, grid_duration=0.25)
        assert abs(offsets[0] - 0.05) < 1e-9
        assert abs(offsets[1] - (-0.05)) < 1e-9

    def test_length(self):
        notes = [Note("C", 5, 0.25) for _ in range(8)]
        offsets = extract_groove(notes)
        assert len(offsets) == 8
