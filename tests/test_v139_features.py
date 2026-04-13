"""Tests for v139.0: auto_accompany, compare_songs."""

import unittest

from code_music import (
    Note,
    Song,
    Track,
    auto_accompany,
    compare_songs,
    scale,
)

# ---------------------------------------------------------------------------
# auto_accompany
# ---------------------------------------------------------------------------


class TestAutoAccompany(unittest.TestCase):
    """Generate full accompaniment from a melody."""

    def _melody(self):
        return [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0), Note("C", 6, 2.0)]

    def test_returns_song(self):
        song = auto_accompany(self._melody(), key="C", seed=42)
        assert isinstance(song, Song)

    def test_has_multiple_tracks(self):
        song = auto_accompany(self._melody(), key="C", genre="pop", seed=42)
        assert len(song.tracks) >= 3  # melody + chords + bass

    def test_melody_track_present(self):
        song = auto_accompany(self._melody(), key="C", seed=42)
        names = [t.name for t in song.tracks]
        assert "melody" in names

    def test_chords_track_present(self):
        song = auto_accompany(self._melody(), key="C", seed=42)
        names = [t.name for t in song.tracks]
        assert "chords" in names

    def test_bass_track_present(self):
        song = auto_accompany(self._melody(), key="C", seed=42)
        names = [t.name for t in song.tracks]
        assert "bass" in names

    def test_drums_for_pop(self):
        song = auto_accompany(self._melody(), key="C", genre="pop", seed=42)
        assert len(song.tracks) >= 4  # melody + chords + bass + drums

    def test_no_drums_for_ambient(self):
        song = auto_accompany(self._melody(), key="C", genre="ambient", seed=42)
        names = [t.name for t in song.tracks]
        assert not any("kick" in n or "snare" in n or "hat" in n for n in names)

    def test_no_drums_for_classical(self):
        song = auto_accompany(self._melody(), key="C", genre="classical", seed=42)
        names = [t.name for t in song.tracks]
        assert not any("kick" in n or "snare" in n or "hat" in n for n in names)

    def test_key_propagated(self):
        song = auto_accompany(self._melody(), key="Bb", seed=42)
        assert song.key_sig == "Bb"

    def test_bpm_propagated(self):
        song = auto_accompany(self._melody(), bpm=90, seed=42)
        assert song.bpm == 90

    def test_custom_title(self):
        song = auto_accompany(self._melody(), title="My Song", seed=42)
        assert song.title == "My Song"

    def test_default_title(self):
        song = auto_accompany(self._melody(), key="G", seed=42)
        assert "G" in song.title

    def test_deterministic(self):
        s1 = auto_accompany(self._melody(), key="C", seed=99)
        s2 = auto_accompany(self._melody(), key="C", seed=99)
        assert len(s1.tracks) == len(s2.tracks)
        assert len(s1.tracks[0].beats) == len(s2.tracks[0].beats)

    def test_auto_key_detection(self):
        # C major melody should detect C
        mel = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0)]
        song = auto_accompany(mel, key=None, seed=42)
        assert isinstance(song, Song)

    def test_long_melody(self):
        mel = scale("A", "pentatonic", octave=5, length=32)
        song = auto_accompany(mel, key="A", genre="jazz", seed=42)
        assert len(song.tracks) >= 3

    def test_all_genres(self):
        mel = self._melody()
        for genre in ["pop", "jazz", "rock", "blues", "classical", "electronic", "ambient"]:
            song = auto_accompany(mel, key="C", genre=genre, seed=42)
            assert isinstance(song, Song), f"{genre} failed"
            assert len(song.tracks) >= 3, f"{genre} should have 3+ tracks"

    def test_imports_from_theory(self):
        from code_music.theory import auto_accompany as aa

        assert callable(aa)


# ---------------------------------------------------------------------------
# compare_songs
# ---------------------------------------------------------------------------


class TestCompareSongs(unittest.TestCase):
    """Compare two Songs across multiple dimensions."""

    def _make_song(self, title, key, bpm, instrument, notes):
        song = Song(title=title, bpm=bpm, key_sig=key)
        tr = song.add_track(Track(name="lead", instrument=instrument))
        for n in notes:
            tr.add(n)
        return song

    def test_returns_dict(self):
        a = self._make_song("A", "C", 120, "piano", [Note("C", 4, 1.0)])
        b = self._make_song("B", "C", 120, "piano", [Note("C", 4, 1.0)])
        result = compare_songs(a, b)
        assert isinstance(result, dict)

    def test_has_expected_keys(self):
        a = self._make_song("A", "C", 120, "piano", [Note("C", 4, 1.0)])
        b = self._make_song("B", "C", 120, "piano", [Note("C", 4, 1.0)])
        result = compare_songs(a, b)
        for key in ["overall_similarity", "dimensions", "metadata", "differences"]:
            assert key in result, f"Missing key: {key}"

    def test_dimensions_present(self):
        a = self._make_song("A", "C", 120, "piano", [Note("C", 4, 1.0)])
        b = self._make_song("B", "C", 120, "piano", [Note("C", 4, 1.0)])
        result = compare_songs(a, b)
        for dim in ["harmonic", "melodic", "rhythmic", "timbral", "structural"]:
            assert dim in result["dimensions"]

    def test_identical_songs_high_similarity(self):
        notes = [Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)]
        a = self._make_song("A", "C", 120, "piano", notes)
        b = self._make_song("B", "C", 120, "piano", notes)
        result = compare_songs(a, b)
        assert result["overall_similarity"] > 0.8

    def test_different_songs_lower_similarity(self):
        a = self._make_song("A", "C", 60, "bass", [Note("C", 2, 4.0)])
        b = self._make_song("B", "G", 180, "sawtooth", [Note("G", 6, 0.25)] * 16)
        result = compare_songs(a, b)
        # Should be less similar than identical
        notes = [Note("C", 4, 1.0)]
        same = compare_songs(
            self._make_song("X", "C", 120, "piano", notes),
            self._make_song("Y", "C", 120, "piano", notes),
        )
        assert result["overall_similarity"] < same["overall_similarity"]

    def test_similarity_range(self):
        a = self._make_song("A", "C", 120, "piano", [Note("C", 4, 1.0)])
        b = self._make_song("B", "G", 90, "bass", [Note("G", 2, 4.0)])
        result = compare_songs(a, b)
        assert 0.0 <= result["overall_similarity"] <= 1.0

    def test_tempo_difference_noted(self):
        a = self._make_song("A", "C", 60, "piano", [Note("C", 4, 1.0)])
        b = self._make_song("B", "C", 180, "piano", [Note("C", 4, 1.0)])
        result = compare_songs(a, b)
        assert any("Tempo" in d for d in result["differences"])

    def test_key_difference_noted(self):
        a = self._make_song("A", "C", 120, "piano", [Note("C", 4, 1.0)])
        b = self._make_song("B", "G", 120, "piano", [Note("G", 4, 1.0)])
        result = compare_songs(a, b)
        assert any("Key" in d for d in result["differences"])

    def test_metadata_present(self):
        a = self._make_song("Song A", "C", 120, "piano", [Note("C", 4, 1.0)])
        b = self._make_song("Song B", "G", 90, "bass", [Note("G", 2, 4.0)])
        result = compare_songs(a, b)
        assert result["metadata"]["a"]["title"] == "Song A"
        assert result["metadata"]["b"]["title"] == "Song B"

    def test_instrument_difference_noted(self):
        a = self._make_song("A", "C", 120, "piano", [Note("C", 4, 1.0)])
        b = self._make_song("B", "C", 120, "bass", [Note("C", 2, 1.0)])
        result = compare_songs(a, b)
        assert any("Only in" in d for d in result["differences"])

    def test_empty_songs(self):
        a = Song(title="A", bpm=120)
        a.add_track(Track())
        b = Song(title="B", bpm=120)
        b.add_track(Track())
        result = compare_songs(a, b)
        assert isinstance(result, dict)
        assert result["overall_similarity"] >= 0.0

    def test_imports_from_theory(self):
        from code_music.theory import compare_songs as cs

        assert callable(cs)


if __name__ == "__main__":
    unittest.main()
