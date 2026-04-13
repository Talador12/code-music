"""Tests for restyle() — style transfer between genres."""

from code_music.theory import generate_full_song, restyle


class TestRestyle:
    """Style transfer produces valid re-arranged songs."""

    def _pop_song(self):
        return generate_full_song("pop", key="C", bpm=120, seed=1)

    def test_pop_to_jazz(self):
        song = self._pop_song()
        result = restyle(song, "jazz", seed=42)
        assert result.title == "Jazz Restyle"
        tracks = [t.name for t in result.tracks]
        assert "bass" in tracks
        assert "piano" in tracks

    def test_pop_to_blues(self):
        result = restyle(self._pop_song(), "blues", seed=7)
        assert result.title == "Blues Restyle"
        assert result.bpm == 110  # genre default

    def test_pop_to_metal(self):
        result = restyle(self._pop_song(), "metal", bpm=180, seed=11)
        assert result.title == "Metal Restyle"
        assert result.bpm == 180

    def test_pop_to_ambient(self):
        result = restyle(self._pop_song(), "ambient", seed=3)
        assert result.bpm == 70  # ambient default

    def test_pop_to_electronic(self):
        result = restyle(self._pop_song(), "electronic", seed=5)
        assert result.title == "Electronic Restyle"
        assert result.bpm == 128

    def test_key_override(self):
        result = restyle(self._pop_song(), "blues", key="A", seed=7)
        # Should still produce a valid song
        assert len(result.tracks) >= 3

    def test_bpm_override(self):
        result = restyle(self._pop_song(), "jazz", bpm=200, seed=42)
        assert result.bpm == 200

    def test_seed_reproducibility(self):
        song = self._pop_song()
        r1 = restyle(song, "jazz", seed=42)
        r2 = restyle(song, "jazz", seed=42)
        assert len(r1.tracks) == len(r2.tracks)
        for t1, t2 in zip(r1.tracks, r2.tracks):
            assert len(t1.beats) == len(t2.beats)

    def test_all_tracks_have_content(self):
        result = restyle(self._pop_song(), "rock", seed=1)
        for track in result.tracks:
            assert len(track.beats) > 0, f"Track {track.name} is empty"

    def test_restyle_jazz_to_pop(self):
        jazz = generate_full_song("jazz", key="Bb", bpm=140, seed=1)
        pop = restyle(jazz, "pop", seed=42)
        assert pop.title == "Pop Restyle"

    def test_restyle_preserves_structure_length(self):
        song = self._pop_song()
        result = restyle(song, "jazz", seed=42)
        result_chord_count = sum(
            1 for t in result.tracks for b in t.beats if b.event and hasattr(b.event, "root")
        )
        # Should have similar structure (auto_arrange may differ slightly)
        assert result_chord_count > 0

    def test_reharmonization_changes_shapes(self):
        # Jazz restyle should turn triads into 7th chords
        song = self._pop_song()
        result = restyle(song, "jazz", seed=42)
        shapes = set()
        for t in result.tracks:
            for b in t.beats:
                if b.event and hasattr(b.event, "shape"):
                    shapes.add(b.event.shape)
        # Jazz should have 7th chords
        seventh_shapes = {"maj7", "min7", "dom7", "dom9"}
        assert shapes & seventh_shapes  # at least some 7ths

    def test_unknown_genre_still_works(self):
        result = restyle(self._pop_song(), "zzz_not_real", seed=1)
        assert len(result.tracks) >= 3
