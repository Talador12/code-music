"""Tests for v160.0: Song.fill_tracks(), 10 new songs."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from code_music import Note, Song, Track, scale


class TestFillTracks(unittest.TestCase):
    """Song.fill_tracks() auto-fills missing instrument roles."""

    def test_fills_bass_and_drums(self):
        song = Song(title="Sketch", bpm=120, key_sig="C")
        lead = song.add_track(Track(name="lead", instrument="sawtooth"))
        lead.extend(scale("C", "major", octave=5, length=16))
        song.fill_tracks(seed=42)
        names = [t.name.lower() for t in song.tracks]
        assert any("bass" in n for n in names)

    def test_fills_chords(self):
        song = Song(title="Sketch", bpm=120, key_sig="C")
        lead = song.add_track(Track(name="lead", instrument="sawtooth"))
        lead.extend(scale("C", "major", octave=5, length=8))
        song.fill_tracks(roles=["chords"], seed=42)
        names = [t.name for t in song.tracks]
        assert "chords" in names

    def test_does_not_duplicate(self):
        song = Song(title="Full", bpm=120, key_sig="C")
        song.add_track(Track(name="lead", instrument="sawtooth"))
        song.add_track(Track(name="bass", instrument="bass"))
        song.add_track(Track(name="chords", instrument="pad"))
        song.add_track(Track(name="kick", instrument="drums_kick"))
        initial = len(song.tracks)
        song.fill_tracks(seed=42)
        assert len(song.tracks) == initial  # nothing added

    def test_returns_self(self):
        song = Song(title="Chain", bpm=120, key_sig="C")
        song.add_track(Track(name="lead", instrument="sawtooth")).add(Note("C", 5, 4.0))
        result = song.fill_tracks(seed=42)
        assert result is song

    def test_genre_affects_output(self):
        s1 = Song(title="Pop", bpm=120, key_sig="C")
        s1.add_track(Track(name="lead", instrument="sawtooth")).add(Note("C", 5, 8.0))
        s1.fill_tracks(genre="pop", seed=42)

        s2 = Song(title="Jazz", bpm=120, key_sig="C")
        s2.add_track(Track(name="lead", instrument="sawtooth")).add(Note("C", 5, 8.0))
        s2.fill_tracks(genre="jazz", seed=42)

        # Both genres should produce multi-track songs
        assert len(s1.tracks) > 1
        assert len(s2.tracks) > 1

    def test_explicit_roles(self):
        song = Song(title="Specific", bpm=120, key_sig="C")
        song.add_track(Track(name="lead", instrument="sawtooth")).add(Note("C", 5, 4.0))
        song.fill_tracks(roles=["bass"], seed=42)
        names = [t.name for t in song.tracks]
        assert "bass" in names
        assert "chords" not in names  # only bass was requested

    def test_no_drums_for_ambient(self):
        song = Song(title="Ambient", bpm=60, key_sig="D")
        song.add_track(Track(name="lead", instrument="triangle")).add(Note("D", 5, 8.0))
        song.fill_tracks(genre="ambient", seed=42)
        instruments = set(t.instrument for t in song.tracks)
        assert not instruments & {"drums_kick", "drums_snare", "drums_hat"}

    def test_empty_song_fills_melody(self):
        song = Song(title="Empty", bpm=120, key_sig="C")
        song.fill_tracks(seed=42)
        assert len(song.tracks) >= 3  # melody + chords + bass (+ maybe drums)


class TestNewSongs(unittest.TestCase):
    """10 new songs load cleanly."""

    def _load(self, name):
        import importlib.util

        path = Path(__file__).parent.parent / "songs" / f"{name}.py"
        spec = importlib.util.spec_from_file_location(name, str(path))
        mod = importlib.util.module_from_spec(spec)
        out = io.StringIO()
        with redirect_stdout(out):
            spec.loader.exec_module(mod)
        return mod

    def test_mixolydian_blues(self):
        assert isinstance(self._load("mixolydian_blues").song, Song)

    def test_ambient_space(self):
        assert isinstance(self._load("ambient_space").song, Song)

    def test_celtic_reel(self):
        assert isinstance(self._load("celtic_reel").song, Song)

    def test_hip_hop_beat(self):
        assert isinstance(self._load("hip_hop_beat").song, Song)

    def test_bossa_sunset(self):
        assert isinstance(self._load("bossa_sunset").song, Song)

    def test_film_score(self):
        assert isinstance(self._load("film_score").song, Song)

    def test_lo_fi_study(self):
        assert isinstance(self._load("lo_fi_study").song, Song)

    def test_progressive_rock(self):
        assert isinstance(self._load("progressive_rock").song, Song)

    def test_minimal_techno(self):
        assert isinstance(self._load("minimal_techno").song, Song)

    def test_country_roads(self):
        assert isinstance(self._load("country_roads").song, Song)


if __name__ == "__main__":
    unittest.main()
