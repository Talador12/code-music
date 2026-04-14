"""Tests for v148.0: Clip.quantize_to_bars, JSON sort_keys, make collab."""

import inspect
import json
import unittest

from code_music import Clip, Note, Song, Track
from code_music.serialization import song_to_json

# ---------------------------------------------------------------------------
# Clip.quantize_to_bars
# ---------------------------------------------------------------------------


class TestClipQuantizeToBars(unittest.TestCase):
    """Snap clip length to bar boundaries."""

    def _clip(self, n_beats):
        tr = Track()
        tr.extend([Note("C", 4, 1.0)] * n_beats)
        return Clip.from_track(tr)

    def test_already_aligned(self):
        clip = self._clip(8)
        q = clip.quantize_to_bars(beats_per_bar=4)
        assert len(q) == 8

    def test_nearest_rounds_up(self):
        clip = self._clip(7)  # 7 beats, nearest bar is 8
        q = clip.quantize_to_bars(beats_per_bar=4, mode="nearest")
        assert len(q) == 8

    def test_nearest_rounds_down(self):
        clip = self._clip(5)  # 5 beats, nearest bar is 4
        q = clip.quantize_to_bars(beats_per_bar=4, mode="nearest")
        assert len(q) == 4

    def test_ceil_pads(self):
        clip = self._clip(5)
        q = clip.quantize_to_bars(beats_per_bar=4, mode="ceil")
        assert len(q) == 8
        # Last 3 beats should be rests
        assert q.beats[5].event is None

    def test_floor_trims(self):
        clip = self._clip(7)
        q = clip.quantize_to_bars(beats_per_bar=4, mode="floor")
        assert len(q) == 4

    def test_floor_minimum_one_bar(self):
        clip = self._clip(2)
        q = clip.quantize_to_bars(beats_per_bar=4, mode="floor")
        assert len(q) == 4  # minimum is one bar

    def test_empty_clip(self):
        clip = Clip()
        q = clip.quantize_to_bars()
        assert len(q) == 0

    def test_different_time_sig(self):
        clip = self._clip(7)
        q = clip.quantize_to_bars(beats_per_bar=3, mode="ceil")
        assert len(q) == 9  # ceil(7/3) * 3 = 9

    def test_preserves_events(self):
        clip = self._clip(5)
        q = clip.quantize_to_bars(beats_per_bar=4, mode="ceil")
        events = q.to_events()
        assert events[0] is not None  # original notes preserved
        assert events[4] is not None
        assert events[5] is None  # padded rest


# ---------------------------------------------------------------------------
# JSON sort_keys
# ---------------------------------------------------------------------------


class TestJSONSortKeys(unittest.TestCase):
    """song_to_json with sort_keys produces diff-friendly output."""

    def _song(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("C", 4, 1.0))
        return song

    def test_sort_keys_parameter_exists(self):
        sig = inspect.signature(song_to_json)
        assert "sort_keys" in sig.parameters

    def test_sorted_json_string(self):
        s = self._song()
        text = song_to_json(s, as_string=True, sort_keys=True)
        data = json.loads(text)
        keys = list(data.keys())
        assert keys == sorted(keys)

    def test_unsorted_default(self):
        s = self._song()
        text = song_to_json(s, as_string=True)
        # Default does not sort - first key should be "version", not alphabetical
        data = json.loads(text)
        assert list(data.keys())[0] == "version"

    def test_sorted_tracks_keys(self):
        s = self._song()
        text = song_to_json(s, as_string=True, sort_keys=True)
        data = json.loads(text)
        if data["tracks"]:
            track_keys = list(data["tracks"][0].keys())
            assert track_keys == sorted(track_keys)


# ---------------------------------------------------------------------------
# Makefile collab target
# ---------------------------------------------------------------------------


class TestMakefileCollab(unittest.TestCase):
    """Makefile has a collab target."""

    def test_collab_target(self):
        from pathlib import Path

        makefile = Path(__file__).parent.parent / "Makefile"
        content = makefile.read_text()
        assert "collab:" in content
        assert "dist/collab" in content


if __name__ == "__main__":
    unittest.main()
