"""Tests for v136.0: generate_form, style_fingerprint, analyze_arrangement."""

import unittest

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    analyze_arrangement,
    generate_form,
    style_fingerprint,
)

# ---------------------------------------------------------------------------
# generate_form
# ---------------------------------------------------------------------------


class TestGenerateForm(unittest.TestCase):
    """Form generator builds complete formal structures as multi-section Songs."""

    def test_sonata_returns_song(self):
        song = generate_form("sonata", key="C", bpm=120, seed=42)
        assert isinstance(song, Song)
        assert "Sonata" in song.title

    def test_rondo_returns_song(self):
        song = generate_form("rondo", key="G", bpm=100, seed=42)
        assert isinstance(song, Song)
        assert "Rondo" in song.title

    def test_aaba_returns_song(self):
        song = generate_form("aaba", key="F", bpm=110, seed=42)
        assert isinstance(song, Song)
        assert "AABA" in song.title

    def test_verse_chorus_returns_song(self):
        song = generate_form("verse_chorus", key="D", bpm=128, seed=42)
        assert isinstance(song, Song)

    def test_binary_returns_song(self):
        song = generate_form("binary", key="A", bpm=90, seed=42)
        assert isinstance(song, Song)
        assert "Binary" in song.title

    def test_ternary_returns_song(self):
        song = generate_form("ternary", key="Bb", bpm=72, seed=42)
        assert isinstance(song, Song)
        assert "Ternary" in song.title

    def test_theme_variations_returns_song(self):
        song = generate_form("theme_variations", key="Eb", bpm=100, seed=42)
        assert isinstance(song, Song)
        assert "Variations" in song.title

    def test_has_multiple_tracks(self):
        song = generate_form("sonata", seed=42)
        assert len(song.tracks) >= 2

    def test_with_melody(self):
        song = generate_form("rondo", include_melody=True, seed=42)
        names = [t.name for t in song.tracks]
        assert "melody" in names

    def test_without_melody(self):
        song = generate_form("rondo", include_melody=False, seed=42)
        names = [t.name for t in song.tracks]
        assert "melody" not in names

    def test_deterministic(self):
        s1 = generate_form("aaba", seed=99)
        s2 = generate_form("aaba", seed=99)
        assert len(s1.tracks[0].beats) == len(s2.tracks[0].beats)

    def test_sonata_longer_than_binary(self):
        sonata = generate_form("sonata", seed=42)
        binary = generate_form("binary", seed=42)
        assert len(sonata.tracks[0].beats) > len(binary.tracks[0].beats)

    def test_bpm_propagated(self):
        song = generate_form("aaba", bpm=90, seed=42)
        assert song.bpm == 90

    def test_key_propagated(self):
        song = generate_form("rondo", key="Bb", seed=42)
        assert song.key_sig == "Bb"

    def test_all_styles_produce_nonempty(self):
        for style in [
            "sonata",
            "rondo",
            "aaba",
            "verse_chorus",
            "binary",
            "ternary",
            "theme_variations",
        ]:
            song = generate_form(style, seed=42)
            assert len(song.tracks) >= 2, f"{style} should have 2+ tracks"
            assert len(song.tracks[0].beats) > 0, f"{style} should have beats"

    def test_unknown_style_defaults_to_sonata(self):
        song = generate_form("nonexistent_style", seed=42)
        assert isinstance(song, Song)
        assert len(song.tracks[0].beats) > 0

    def test_custom_chords_per_phrase(self):
        short = generate_form("binary", chords_per_phrase=2, seed=42)
        long = generate_form("binary", chords_per_phrase=8, seed=42)
        assert len(long.tracks[0].beats) > len(short.tracks[0].beats)

    def test_imports_from_theory(self):
        from code_music.theory import generate_form as gf

        assert callable(gf)


# ---------------------------------------------------------------------------
# style_fingerprint
# ---------------------------------------------------------------------------


class TestStyleFingerprint(unittest.TestCase):
    """Style fingerprint extracts multi-dimensional feature vectors."""

    def _simple_song(self):
        song = Song(title="Test", bpm=120, key_sig="C")
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.extend([Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)])
        return song

    def test_returns_dict(self):
        fp = style_fingerprint(self._simple_song())
        assert isinstance(fp, dict)

    def test_has_all_categories(self):
        fp = style_fingerprint(self._simple_song())
        for cat in [
            "harmonic",
            "melodic",
            "rhythmic",
            "timbral",
            "dynamic",
            "structural",
            "register",
            "density",
            "vector",
        ]:
            assert cat in fp, f"Missing category: {cat}"

    def test_vector_is_flat_list(self):
        fp = style_fingerprint(self._simple_song())
        assert isinstance(fp["vector"], list)
        assert all(isinstance(v, float) for v in fp["vector"])

    def test_vector_length_consistent(self):
        fp = style_fingerprint(self._simple_song())
        expected = sum(len(v) for k, v in fp.items() if k != "vector" and isinstance(v, dict))
        assert len(fp["vector"]) == expected

    def test_melodic_features_range(self):
        fp = style_fingerprint(self._simple_song())
        assert fp["melodic"]["pitch_range"] >= 0
        assert 0.0 <= fp["melodic"]["step_ratio"] <= 1.0
        assert 0.0 <= fp["melodic"]["leap_ratio"] <= 1.0

    def test_with_chords(self):
        song = Song(title="Chords", bpm=120, key_sig="C")
        tr = song.add_track(Track(name="chords", instrument="piano"))
        tr.add(Chord("C", "maj", 4, duration=4.0))
        tr.add(Chord("G", "dom7", 4, duration=4.0))
        fp = style_fingerprint(song)
        assert fp["harmonic"]["root_diversity"] > 0

    def test_empty_song(self):
        song = Song(title="Empty", bpm=120)
        song.add_track(Track())
        fp = style_fingerprint(song)
        assert isinstance(fp, dict)
        assert fp["structural"]["track_count"] == 1

    def test_different_songs_different_vectors(self):
        song1 = Song(title="Low", bpm=60, key_sig="C")
        tr1 = song1.add_track(Track(instrument="bass"))
        tr1.extend([Note("C", 2, 4.0), Note("G", 2, 4.0)])

        song2 = Song(title="High", bpm=180, key_sig="G")
        tr2 = song2.add_track(Track(instrument="sawtooth"))
        tr2.extend([Note("G", 6, 0.25)] * 16)

        fp1 = style_fingerprint(song1)
        fp2 = style_fingerprint(song2)
        assert fp1["vector"] != fp2["vector"]

    def test_register_features(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track())
        tr.add(Note("C", 3, 1.0))
        tr.add(Note("C", 6, 1.0))
        fp = style_fingerprint(song)
        assert fp["register"]["register_span"] > 0

    def test_crescendo_detected(self):
        song = Song(title="Cresc", bpm=120)
        tr = song.add_track(Track())
        for i in range(8):
            tr.add(Note("C", 4, 1.0, velocity=0.3 + i * 0.08))
        fp = style_fingerprint(song)
        assert fp["dynamic"]["has_crescendo"] == 1.0

    def test_imports_from_theory(self):
        from code_music.theory import style_fingerprint as sf

        assert callable(sf)


# ---------------------------------------------------------------------------
# analyze_arrangement
# ---------------------------------------------------------------------------


class TestAnalyzeArrangement(unittest.TestCase):
    """Arrangement analyzer detects track roles and balance issues."""

    def test_returns_dict(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("C", 5, 2.0))
        result = analyze_arrangement(song)
        assert isinstance(result, dict)

    def test_has_expected_keys(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("C", 5, 2.0))
        result = analyze_arrangement(song)
        for key in [
            "tracks",
            "roles",
            "register_usage",
            "voice_crossings",
            "range_violations",
            "frequency_balance",
            "suggestions",
            "score",
        ]:
            assert key in result, f"Missing key: {key}"

    def test_single_track_analysis(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("C", 5, 2.0))
        result = analyze_arrangement(song)
        assert len(result["tracks"]) == 1
        assert result["tracks"][0]["name"] == "lead"

    def test_role_detection_bass(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track(name="bass", instrument="bass"))
        tr.add(Note("C", 2, 2.0))
        result = analyze_arrangement(song)
        assert "bass" in result["roles"]

    def test_role_detection_melody(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="sawtooth"))
        tr.extend([Note("C", 5, 0.5), Note("E", 5, 0.5)])
        result = analyze_arrangement(song)
        assert "melody" in result["roles"]

    def test_role_detection_rhythm(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track(name="kick", instrument="drums_kick"))
        tr.add(Note("C", 4, 1.0))
        result = analyze_arrangement(song)
        assert "rhythm" in result["roles"]

    def test_frequency_balance_keys(self):
        song = Song(title="Full", bpm=120)
        bass = song.add_track(Track(name="bass", instrument="bass"))
        bass.add(Note("C", 2, 4.0))
        lead = song.add_track(Track(name="lead", instrument="piano"))
        lead.add(Note("C", 5, 4.0))
        result = analyze_arrangement(song)
        assert "low" in result["frequency_balance"]
        assert "mid" in result["frequency_balance"]
        assert "high" in result["frequency_balance"]

    def test_score_range(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("C", 5, 2.0))
        result = analyze_arrangement(song)
        assert 0 <= result["score"] <= 100

    def test_full_arrangement_scores_higher(self):
        minimal = Song(title="Minimal", bpm=120)
        tr = minimal.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("C", 5, 2.0))

        full = Song(title="Full", bpm=120)
        bass = full.add_track(Track(name="bass", instrument="bass"))
        bass.add(Note("C", 2, 2.0))
        lead = full.add_track(Track(name="lead", instrument="sawtooth"))
        lead.extend([Note("C", 5, 0.5), Note("E", 5, 0.5)])
        kick = full.add_track(Track(name="kick", instrument="drums_kick"))
        kick.add(Note("C", 4, 1.0))

        assert analyze_arrangement(full)["score"] > analyze_arrangement(minimal)["score"]

    def test_suggestions_for_missing_bass(self):
        song = Song(title="No Bass", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("C", 5, 2.0))
        result = analyze_arrangement(song)
        assert any("bass" in s.lower() for s in result["suggestions"])

    def test_empty_track(self):
        song = Song(title="Empty", bpm=120)
        song.add_track(Track())
        result = analyze_arrangement(song)
        assert isinstance(result, dict)
        assert result["score"] >= 0

    def test_register_usage_populated(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track(instrument="piano"))
        tr.extend([Note("C", 3, 1.0), Note("C", 5, 1.0)])
        result = analyze_arrangement(song)
        assert len(result["register_usage"]) >= 1

    def test_imports_from_theory(self):
        from code_music.theory import analyze_arrangement as aa

        assert callable(aa)


if __name__ == "__main__":
    unittest.main()
