"""Tests for v146.0: Session mute/solo, Clip crossfade, new songs."""

import io
import unittest
from contextlib import redirect_stdout

from code_music import Clip, Note, Session, Song, Track

# ---------------------------------------------------------------------------
# Session.stop_track
# ---------------------------------------------------------------------------


class TestSessionStopTrack(unittest.TestCase):
    def _clip(self):
        tr = Track()
        tr.extend([Note("C", 4, 1.0)] * 4)
        return Clip.from_track(tr)

    def test_stop_track(self):
        s = Session(bpm=120)
        s.add_track("drums")
        s.set_clip("drums", 0, self._clip())
        s.launch_scene(0)
        assert s.grid["drums"][0].is_playing
        s.stop_track("drums")
        assert not s.grid["drums"][0].is_playing

    def test_stop_unknown_track(self):
        s = Session(bpm=120)
        s.stop_track("nonexistent")  # should not crash


# ---------------------------------------------------------------------------
# Session mute/solo
# ---------------------------------------------------------------------------


class TestSessionMuteSolo(unittest.TestCase):
    def _clip(self, pitch="C"):
        tr = Track()
        tr.extend([Note(pitch, 4, 1.0)] * 4)
        return Clip.from_track(tr)

    def test_mute_zeroes_volume(self):
        s = Session(bpm=120, sample_rate=22050)
        s.add_track("drums", instrument="drums_kick")
        s.add_track("bass", instrument="bass")
        s.set_clip("drums", 0, self._clip())
        s.set_clip("bass", 0, self._clip("E"))
        s.mute("drums")
        song = s.render()
        # Muted track should have volume 0
        drum_track = [t for t in song.tracks if t.name == "drums"][0]
        assert drum_track.volume == 0.0

    def test_unmute_restores(self):
        s = Session(bpm=120, sample_rate=22050)
        s.add_track("drums", instrument="drums_kick", volume=0.8)
        s.set_clip("drums", 0, self._clip())
        s.mute("drums")
        s.unmute("drums")
        song = s.render()
        drum_track = [t for t in song.tracks if t.name == "drums"][0]
        assert drum_track.volume == 0.8

    def test_solo_mutes_others(self):
        s = Session(bpm=120, sample_rate=22050)
        s.add_track("drums", instrument="drums_kick")
        s.add_track("bass", instrument="bass")
        s.set_clip("drums", 0, self._clip())
        s.set_clip("bass", 0, self._clip("E"))
        s.solo("bass")
        song = s.render()
        drum_track = [t for t in song.tracks if t.name == "drums"][0]
        bass_track = [t for t in song.tracks if t.name == "bass"][0]
        assert drum_track.volume == 0.0
        assert bass_track.volume > 0.0

    def test_unsolo_restores(self):
        s = Session(bpm=120, sample_rate=22050)
        s.add_track("drums", instrument="drums_kick", volume=0.8)
        s.add_track("bass", instrument="bass")
        s.set_clip("drums", 0, self._clip())
        s.set_clip("bass", 0, self._clip("E"))
        s.solo("bass")
        s.unsolo("bass")
        song = s.render()
        drum_track = [t for t in song.tracks if t.name == "drums"][0]
        assert drum_track.volume == 0.8


# ---------------------------------------------------------------------------
# Session set_volume / set_pan
# ---------------------------------------------------------------------------


class TestSessionMixControls(unittest.TestCase):
    def _clip(self):
        tr = Track()
        tr.extend([Note("C", 4, 1.0)] * 4)
        return Clip.from_track(tr)

    def test_set_volume(self):
        s = Session(bpm=120, sample_rate=22050)
        s.add_track("lead", volume=0.5)
        s.set_clip("lead", 0, self._clip())
        s.set_volume("lead", 0.3)
        song = s.render()
        assert song.tracks[0].volume == 0.3

    def test_set_pan(self):
        s = Session(bpm=120, sample_rate=22050)
        s.add_track("lead")
        s.set_clip("lead", 0, self._clip())
        s.set_pan("lead", -0.5)
        song = s.render()
        assert song.tracks[0].pan == -0.5

    def test_volume_clamped(self):
        s = Session(bpm=120)
        s.add_track("lead")
        s.set_volume("lead", 2.0)
        assert s._volumes["lead"] == 1.0

    def test_pan_clamped(self):
        s = Session(bpm=120)
        s.add_track("lead")
        s.set_pan("lead", -5.0)
        assert s._pans["lead"] == -1.0


# ---------------------------------------------------------------------------
# Clip.crossfade
# ---------------------------------------------------------------------------


class TestClipCrossfade(unittest.TestCase):
    def _clip(self, pitches, dur=1.0):
        tr = Track()
        for p in pitches:
            tr.add(Note(p, 4, dur, velocity=70))
        return Clip.from_track(tr)

    def test_crossfade_length(self):
        a = self._clip(["C", "D", "E", "F"])
        b = self._clip(["G", "A", "B", "C"])
        xf = a.crossfade(b, overlap_beats=2)
        # 4 + 4 - 2 overlap = 6
        assert len(xf) == 6

    def test_crossfade_no_overlap(self):
        a = self._clip(["C", "D"])
        b = self._clip(["E", "F"])
        xf = a.crossfade(b, overlap_beats=0)
        assert len(xf) == 4  # just concatenated

    def test_crossfade_full_overlap(self):
        a = self._clip(["C", "D", "E", "F"])
        b = self._clip(["G", "A", "B", "C"])
        xf = a.crossfade(b, overlap_beats=4)
        assert len(xf) == 4  # fully overlapped

    def test_crossfade_preserves_events(self):
        a = self._clip(["C", "D", "E", "F"])
        b = self._clip(["G", "A", "B", "C"])
        xf = a.crossfade(b, overlap_beats=1)
        events = xf.to_events()
        assert all(e is not None for e in events)

    def test_crossfade_with_different_lengths(self):
        a = self._clip(["C", "D", "E"])
        b = self._clip(["G", "A", "B", "C", "D"])
        xf = a.crossfade(b, overlap_beats=2)
        assert len(xf) == 6  # 3 + 5 - 2 = 6


# ---------------------------------------------------------------------------
# New songs load without errors
# ---------------------------------------------------------------------------


class TestNewSongs(unittest.TestCase):
    """All 5 new songs define a `song` variable and load cleanly."""

    def _load(self, name):
        import importlib.util
        from pathlib import Path

        path = Path(__file__).parent.parent / "songs" / f"{name}.py"
        spec = importlib.util.spec_from_file_location(name, str(path))
        mod = importlib.util.module_from_spec(spec)
        out = io.StringIO()
        with redirect_stdout(out):
            spec.loader.exec_module(mod)
        return mod

    def test_session_looper(self):
        mod = self._load("session_looper")
        assert isinstance(mod.song, Song)
        assert len(mod.song.tracks) >= 2

    def test_clip_remix(self):
        mod = self._load("clip_remix")
        assert isinstance(mod.song, Song)

    def test_sidechain_pump(self):
        mod = self._load("sidechain_pump")
        assert isinstance(mod.song, Song)
        assert len(mod.song.tracks) >= 4

    def test_mute_solo_mix(self):
        mod = self._load("mute_solo_mix")
        assert isinstance(mod.song, Song)

    def test_crossfade_journey(self):
        mod = self._load("crossfade_journey")
        assert isinstance(mod.song, Song)


if __name__ == "__main__":
    unittest.main()
