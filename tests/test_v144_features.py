"""Tests for v144.0: Clip system, CLI --merge, automation example."""

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from code_music import Clip, Note, Track

# ---------------------------------------------------------------------------
# Clip
# ---------------------------------------------------------------------------


class TestClipFromTrack(unittest.TestCase):
    """Extract clips from tracks."""

    def _track(self):
        tr = Track(name="lead", instrument="piano")
        tr.extend([Note("C", 4, 1.0), Note("D", 4, 1.0), Note("E", 4, 1.0), Note("F", 4, 1.0)])
        return tr

    def test_full_extract(self):
        clip = Clip.from_track(self._track())
        assert len(clip) == 4

    def test_range_extract(self):
        clip = Clip.from_track(self._track(), start_beat=1, end_beat=3)
        assert len(clip) == 2

    def test_source_name(self):
        clip = Clip.from_track(self._track())
        assert clip.source == "lead"

    def test_custom_name(self):
        clip = Clip.from_track(self._track(), name="riff")
        assert clip.name == "riff"

    def test_deep_copy(self):
        tr = self._track()
        clip = Clip.from_track(tr)
        tr.beats.clear()
        assert len(clip) == 4  # clip is independent


class TestClipLoop(unittest.TestCase):
    """Loop clips N times."""

    def test_loop_doubles(self):
        tr = Track()
        tr.extend([Note("C", 4, 1.0), Note("D", 4, 1.0)])
        clip = Clip.from_track(tr)
        looped = clip.loop(3)
        assert len(looped) == 6

    def test_loop_preserves_events(self):
        tr = Track()
        tr.extend([Note("C", 4, 1.0)])
        clip = Clip.from_track(tr)
        looped = clip.loop(4)
        events = looped.to_events()
        assert all(e.pitch == "C" for e in events)

    def test_loop_one(self):
        tr = Track()
        tr.extend([Note("C", 4, 1.0)])
        clip = Clip.from_track(tr)
        assert len(clip.loop(1)) == 1


class TestClipReverse(unittest.TestCase):
    """Reverse clip beat order."""

    def test_reverse(self):
        tr = Track()
        tr.extend([Note("C", 4, 1.0), Note("D", 4, 1.0), Note("E", 4, 1.0)])
        clip = Clip.from_track(tr)
        rev = clip.reverse()
        events = rev.to_events()
        assert events[0].pitch == "E"
        assert events[2].pitch == "C"

    def test_reverse_preserves_length(self):
        tr = Track()
        tr.extend([Note("C", 4, 1.0)] * 5)
        clip = Clip.from_track(tr)
        assert len(clip.reverse()) == 5


class TestClipTrim(unittest.TestCase):
    """Trim clips to a sub-range."""

    def test_trim(self):
        tr = Track()
        tr.extend([Note("C", 4, 1.0)] * 8)
        clip = Clip.from_track(tr)
        trimmed = clip.trim(2, 5)
        assert len(trimmed) == 3

    def test_trim_from_start(self):
        tr = Track()
        tr.extend([Note("C", 4, 1.0)] * 4)
        clip = Clip.from_track(tr)
        assert len(clip.trim(end=2)) == 2


class TestClipToEvents(unittest.TestCase):
    """Convert clip beats back to events."""

    def test_to_events(self):
        tr = Track()
        tr.extend([Note("C", 4, 1.0), Note("D", 4, 2.0)])
        clip = Clip.from_track(tr)
        events = clip.to_events()
        assert len(events) == 2
        assert events[0].pitch == "C"
        assert events[1].duration == 2.0

    def test_extend_track_from_clip(self):
        tr = Track()
        tr.add(Note("C", 4, 1.0))
        clip = Clip.from_track(tr)
        tr.extend(clip.loop(3).to_events())
        assert len(tr.beats) == 4  # 1 original + 3 looped


class TestClipDuration(unittest.TestCase):
    """Clip duration calculation."""

    def test_duration(self):
        tr = Track()
        tr.extend([Note("C", 4, 1.0), Note("D", 4, 2.0)])
        clip = Clip.from_track(tr)
        assert clip.duration == 3.0

    def test_empty_clip(self):
        clip = Clip()
        assert clip.duration == 0.0
        assert len(clip) == 0


class TestClipRepr(unittest.TestCase):
    """Clip string representation."""

    def test_repr(self):
        tr = Track(name="bass")
        tr.add(Note("C", 2, 1.0))
        clip = Clip.from_track(tr)
        r = repr(clip)
        assert "bass" in r
        assert "1 beats" in r


# ---------------------------------------------------------------------------
# CLI --merge
# ---------------------------------------------------------------------------


class TestCLIMerge(unittest.TestCase):
    """CLI --merge flag."""

    def test_merge_in_help(self):
        from code_music.cli import main

        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                main(["--help"])
            except SystemExit:
                pass
        combined = out.getvalue() + err.getvalue()
        assert "merge" in combined.lower()


# ---------------------------------------------------------------------------
# Automation example runs
# ---------------------------------------------------------------------------


class TestAutomationExample(unittest.TestCase):
    """examples/15_automation.py runs without errors."""

    def test_example_runs(self):
        import importlib.util
        from pathlib import Path

        example = Path(__file__).parent.parent / "examples" / "15_automation.py"
        spec = importlib.util.spec_from_file_location("example_15", str(example))
        mod = importlib.util.module_from_spec(spec)
        out = io.StringIO()
        with redirect_stdout(out):
            spec.loader.exec_module(mod)
        assert hasattr(mod, "song")
        assert len(mod.song.tracks) >= 4


# ---------------------------------------------------------------------------
# Import verification
# ---------------------------------------------------------------------------


class TestClipImports(unittest.TestCase):
    """Clip is importable from top-level."""

    def test_import(self):
        from code_music import Clip

        assert Clip is not None

    def test_from_engine(self):
        from code_music.engine import Clip

        assert Clip is not None


if __name__ == "__main__":
    unittest.main()
