"""Tests for v169.0: wt_scan/spectral presets, scales, chords, CLI discovery."""

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from code_music.engine import CHORD_SHAPES, SCALES
from code_music.sound_design import PRESETS


class TestScaleExpansion(unittest.TestCase):
    def test_scale_count(self):
        assert len(SCALES) >= 53, f"Only {len(SCALES)} scales"

    def test_new_scales_exist(self):
        for name in [
            "aeolian",
            "acoustic",
            "altered",
            "double_harmonic",
            "spanish_gypsy",
            "arabian",
            "balinese",
            "chinese",
            "egyptian",
            "iwato",
            "kumoi",
            "pelog",
            "prometheus",
            "tritone",
            "half_diminished",
        ]:
            assert name in SCALES, f"Missing scale: {name}"

    def test_all_scales_are_lists(self):
        for name, intervals in SCALES.items():
            assert isinstance(intervals, list), f"{name} is not a list"
            assert all(isinstance(i, int) for i in intervals), f"{name} has non-int"


class TestChordExpansion(unittest.TestCase):
    def test_chord_count(self):
        assert len(CHORD_SHAPES) >= 36, f"Only {len(CHORD_SHAPES)} chords"

    def test_new_chords_exist(self):
        for name in [
            "min11",
            "min13",
            "7#11",
            "maj7#11",
            "7alt",
            "dim_maj7",
            "aug_maj7",
            "quartal",
        ]:
            assert name in CHORD_SHAPES, f"Missing chord: {name}"

    def test_all_chords_are_lists(self):
        for name, intervals in CHORD_SHAPES.items():
            assert isinstance(intervals, list), f"{name} is not a list"


class TestWTScanPresets(unittest.TestCase):
    def test_presets_exist(self):
        for name in [
            "wt_scan_evolve",
            "wt_scan_pad",
            "wt_scan_lead",
            "wt_scan_bass",
            "wt_scan_texture",
        ]:
            assert name in PRESETS, f"Missing: {name}"

    def test_all_render(self):
        for name in [
            "wt_scan_evolve",
            "wt_scan_pad",
            "wt_scan_lead",
            "wt_scan_bass",
            "wt_scan_texture",
        ]:
            audio = PRESETS[name].render(440.0, 0.3, 22050)
            assert len(audio) > 0, f"{name} silent"


class TestSpectralPresets(unittest.TestCase):
    def test_presets_exist(self):
        for name in ["spectral_frozen", "spectral_shifted", "spectral_smeared"]:
            assert name in PRESETS, f"Missing: {name}"

    def test_all_render(self):
        for name in ["spectral_frozen", "spectral_shifted", "spectral_smeared"]:
            audio = PRESETS[name].render(440.0, 0.3, 22050)
            assert len(audio) > 0, f"{name} silent"


class TestTotalPresetCount(unittest.TestCase):
    def test_core_count(self):
        assert len(PRESETS) >= 59, f"Only {len(PRESETS)} core presets"


class TestCLIDiscovery(unittest.TestCase):
    def _run_cli(self, args):
        from code_music.cli import main

        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                main(args)
            except SystemExit:
                pass
        return out.getvalue() + err.getvalue()

    def test_list_scales(self):
        output = self._run_cli(["--list-scales"])
        assert "major" in output
        assert "pentatonic" in output
        assert "aeolian" in output

    def test_list_chords(self):
        output = self._run_cli(["--list-chords"])
        assert "maj" in output
        assert "dom7" in output
        assert "quartal" in output

    def test_help_has_new_flags(self):
        output = self._run_cli(["--help"])
        assert "list-scales" in output
        assert "list-chords" in output
        assert "track-waveforms" in output
        assert "sheet-music" in output


if __name__ == "__main__":
    unittest.main()
