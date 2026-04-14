"""Tests for v145.0: ClipSlot, Session, export_stems improvements."""

import tempfile
import unittest

from code_music import Clip, ClipSlot, Note, Session, Song, Track

# ---------------------------------------------------------------------------
# ClipSlot
# ---------------------------------------------------------------------------


class TestClipSlot(unittest.TestCase):
    """ClipSlot holds a Clip with play/stop/queue state."""

    def _clip(self):
        tr = Track()
        tr.extend([Note("C", 4, 1.0), Note("D", 4, 1.0)])
        return Clip.from_track(tr)

    def test_default_stopped(self):
        slot = ClipSlot(clip=self._clip())
        assert slot.state == "stopped"
        assert not slot.is_playing

    def test_play(self):
        slot = ClipSlot(clip=self._clip())
        slot.play()
        assert slot.is_playing

    def test_stop(self):
        slot = ClipSlot(clip=self._clip())
        slot.play()
        slot.stop()
        assert not slot.is_playing

    def test_queue(self):
        slot = ClipSlot(clip=self._clip())
        slot.queue()
        assert slot.state == "queued"

    def test_empty_slot(self):
        slot = ClipSlot()
        assert slot.is_empty
        slot.play()  # should not crash
        assert not slot.is_playing  # stays stopped, no clip

    def test_repr_with_clip(self):
        slot = ClipSlot(clip=self._clip())
        assert "stopped" in repr(slot)

    def test_repr_empty(self):
        assert "empty" in repr(ClipSlot())


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------


class TestSession(unittest.TestCase):
    """Ableton-style session grid with clips."""

    def _clip(self, pitch="C", beats=4):
        tr = Track()
        tr.extend([Note(pitch, 4, 1.0)] * beats)
        return Clip.from_track(tr)

    def test_add_track(self):
        s = Session(bpm=120)
        s.add_track("drums", instrument="drums_kick")
        assert "drums" in s.track_names
        assert len(s.track_names) == 1

    def test_add_scene(self):
        s = Session(bpm=120)
        s.add_track("drums")
        idx = s.add_scene()
        assert idx == 0 or idx >= 0

    def test_set_clip(self):
        s = Session(bpm=120)
        s.add_track("drums")
        s.set_clip("drums", 0, self._clip())
        assert not s.grid["drums"][0].is_empty

    def test_set_clip_auto_expands(self):
        s = Session(bpm=120)
        s.add_track("drums")
        s.set_clip("drums", 5, self._clip())
        assert s.scene_count >= 6

    def test_set_clip_unknown_track(self):
        s = Session(bpm=120)
        with self.assertRaises(ValueError):
            s.set_clip("nonexistent", 0, self._clip())

    def test_launch_scene(self):
        s = Session(bpm=120)
        s.add_track("drums")
        s.set_clip("drums", 0, self._clip())
        s.launch_scene(0)
        assert s.grid["drums"][0].is_playing

    def test_stop_all(self):
        s = Session(bpm=120)
        s.add_track("drums")
        s.add_track("bass")
        s.set_clip("drums", 0, self._clip())
        s.set_clip("bass", 0, self._clip("E"))
        s.launch_scene(0)
        s.stop_all()
        assert not s.grid["drums"][0].is_playing
        assert not s.grid["bass"][0].is_playing

    def test_render_basic(self):
        s = Session(bpm=120, sample_rate=22050)
        s.add_track("drums", instrument="drums_kick")
        s.set_clip("drums", 0, self._clip())
        song = s.render()
        assert isinstance(song, Song)
        assert len(song.tracks) == 1
        assert len(song.tracks[0].beats) == 4

    def test_render_scene_order(self):
        s = Session(bpm=120, sample_rate=22050)
        s.add_track("drums", instrument="drums_kick")
        s.set_clip("drums", 0, self._clip("C", 2))
        s.set_clip("drums", 1, self._clip("D", 2))
        song = s.render(scene_order=[0, 1, 0])
        assert len(song.tracks[0].beats) == 6  # 2+2+2

    def test_render_loops_per_scene(self):
        s = Session(bpm=120, sample_rate=22050)
        s.add_track("drums", instrument="drums_kick")
        s.set_clip("drums", 0, self._clip("C", 4))
        song = s.render(loops_per_scene=2)
        assert len(song.tracks[0].beats) == 8  # 4 * 2

    def test_render_multi_track(self):
        s = Session(bpm=120, sample_rate=22050)
        s.add_track("drums", instrument="drums_kick")
        s.add_track("bass", instrument="bass")
        s.set_clip("drums", 0, self._clip("C", 4))
        s.set_clip("bass", 0, self._clip("E", 4))
        song = s.render()
        assert len(song.tracks) == 2

    def test_render_empty_slots_get_silence(self):
        s = Session(bpm=120, sample_rate=22050)
        s.add_track("drums", instrument="drums_kick")
        s.add_track("bass", instrument="bass")
        s.set_clip("drums", 0, self._clip("C", 4))
        # bass has no clip in scene 0
        song = s.render()
        assert len(song.tracks) == 2

    def test_repr(self):
        s = Session(bpm=120)
        s.add_track("drums")
        s.set_clip("drums", 0, self._clip())
        r = repr(s)
        assert "1 tracks" in r
        assert "1 clips" in r


# ---------------------------------------------------------------------------
# export_stems improvements
# ---------------------------------------------------------------------------


class TestExportStemsImprovements(unittest.TestCase):
    """export_stems with effects and title prefix."""

    def _song(self):
        song = Song(title="Test Song", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(name="lead", instrument="sine"))
        tr.add(Note("C", 4, 2.0))
        return song

    def test_title_prefix(self):
        song = self._song()
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = song.export_stems(tmpdir, use_title_prefix=True)
            assert len(paths) == 1
            assert "test_song_lead" in paths[0].name

    def test_no_title_prefix(self):
        song = self._song()
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = song.export_stems(tmpdir, use_title_prefix=False)
            assert paths[0].name == "lead.wav"

    def test_include_effects_flag(self):
        import inspect

        sig = inspect.signature(Song.export_stems)
        assert "include_effects" in sig.parameters


# ---------------------------------------------------------------------------
# Import verification
# ---------------------------------------------------------------------------


class TestImports(unittest.TestCase):
    """New classes are importable from top-level."""

    def test_clip_slot(self):
        from code_music import ClipSlot

        assert ClipSlot is not None

    def test_session(self):
        from code_music import Session

        assert Session is not None

    def test_from_engine(self):
        from code_music.engine import ClipSlot, Session

        assert ClipSlot is not None
        assert Session is not None


if __name__ == "__main__":
    unittest.main()
