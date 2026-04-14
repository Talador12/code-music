"""Tests for v163.0: sheet music SVG, room model reverb."""

import unittest

import numpy as np

from code_music import Chord, Note, Song, Track, to_sheet_music
from code_music.effects import room_reverb


class TestSheetMusic(unittest.TestCase):
    """Sheet music SVG notation renderer."""

    def _song(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track(name="lead"))
        tr.extend([Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 2.0)])
        return song

    def test_returns_svg(self):
        svg = to_sheet_music(self._song())
        assert "<svg" in svg and "</svg>" in svg

    def test_has_note_heads(self):
        svg = to_sheet_music(self._song())
        assert "<ellipse" in svg

    def test_has_staff_lines(self):
        svg = to_sheet_music(self._song())
        # 5 staff lines
        assert svg.count('stroke-width="0.8"') >= 5

    def test_has_bar_lines(self):
        svg = to_sheet_music(self._song())
        assert svg.count('stroke-width="0.5"') >= 1

    def test_has_stems(self):
        svg = to_sheet_music(self._song())
        assert svg.count('stroke-width="1"') >= 1

    def test_contains_title(self):
        svg = to_sheet_music(self._song())
        assert "Test" in svg

    def test_with_chords(self):
        song = Song(title="Chords", bpm=120)
        tr = song.add_track(Track())
        tr.add(Chord("C", "maj", 4, duration=4.0))
        svg = to_sheet_music(song)
        assert "<ellipse" in svg

    def test_with_accidentals(self):
        song = Song(title="Sharps", bpm=120)
        tr = song.add_track(Track())
        tr.add(Note("F#", 4, 1.0))
        svg = to_sheet_music(song)
        assert "\u266f" in svg  # sharp symbol

    def test_invalid_track_index(self):
        svg = to_sheet_music(self._song(), track_index=99)
        assert "No track" in svg

    def test_write_to_file(self):
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            to_sheet_music(self._song(), path=f.name)
            assert "<svg" in Path(f.name).read_text()
            Path(f.name).unlink()

    def test_import(self):
        from code_music import to_sheet_music as tsm

        assert callable(tsm)


class TestRoomReverb(unittest.TestCase):
    """Room model reverb from dimensions."""

    def test_stereo_shape(self):
        audio = np.random.randn(22050, 2) * 0.1
        result = room_reverb(audio, 22050, width=5, depth=7, height=3)
        assert result.shape == audio.shape

    def test_mono_shape(self):
        audio = np.random.randn(22050) * 0.1
        result = room_reverb(audio, 22050)
        assert result.shape == audio.shape

    def test_wet_zero_is_dry(self):
        audio = np.random.randn(4410, 2) * 0.3
        result = room_reverb(audio, 22050, wet=0.0)
        np.testing.assert_array_almost_equal(result, audio)

    def test_output_not_silent(self):
        audio = np.zeros((22050, 2))
        audio[:500] = 0.5  # impulse
        result = room_reverb(audio, 22050, wet=0.5)
        # Reverb tail should extend beyond the impulse
        assert np.max(np.abs(result[5000:])) > 0.0001

    def test_small_room_vs_large(self):
        audio = np.zeros(22050)
        audio[:100] = 0.5
        small = room_reverb(audio, 22050, width=2, depth=3, height=2.5, wet=0.5)
        large = room_reverb(audio, 22050, width=20, depth=30, height=10, wet=0.5)
        # Large room should have more reverb energy later
        assert not np.array_equal(small, large)

    def test_high_absorption(self):
        audio = np.random.randn(22050, 2) * 0.1
        result = room_reverb(audio, 22050, absorption=0.9, wet=0.5)
        assert result.shape == audio.shape


if __name__ == "__main__":
    unittest.main()
