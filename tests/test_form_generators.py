"""Tests for form generators: generate_canon, generate_sonata_form, generate_rondo."""

import pytest

from code_music import Note, Song, generate_canon, generate_sonata_form, generate_rondo


# ---------------------------------------------------------------------------
# generate_canon
# ---------------------------------------------------------------------------


class TestGenerateCanon:
    """Canon/Round form generator produces valid multi-track Songs."""

    def test_basic_canon(self):
        song = generate_canon(voices=3, key="D", seed=42)
        assert isinstance(song, Song)
        assert "Canon" in song.title
        assert "D" in song.title
        assert len(song.tracks) == 3

    def test_canon_with_custom_melody(self):
        melody = [
            Note("C", 5, 1.0),
            Note("E", 5, 1.0),
            Note("G", 5, 1.0),
            Note("C", 6, 2.0),
        ]
        song = generate_canon(melody=melody, voices=2, key="C", seed=1)
        assert len(song.tracks) == 2

    def test_voice_counts(self):
        for v in [2, 3, 4, 5]:
            song = generate_canon(voices=v, key="C", seed=42)
            assert len(song.tracks) == v

    def test_minimum_voices_clamped(self):
        """Voices below 2 are clamped to 2."""
        song = generate_canon(voices=1, key="C", seed=42)
        assert len(song.tracks) == 2

    def test_maximum_voices_clamped(self):
        """Voices above 6 are clamped to 6."""
        song = generate_canon(voices=10, key="C", seed=42)
        assert len(song.tracks) == 6

    def test_canon_at_fifth(self):
        """Canon at the fifth transposes each voice by 7 semitones."""
        song = generate_canon(voices=2, key="C", interval=7, seed=42)
        assert len(song.tracks) == 2

    def test_canon_at_unison(self):
        """Canon at unison uses interval=0 (default)."""
        song = generate_canon(voices=3, key="C", interval=0, seed=42)
        assert len(song.tracks) == 3

    def test_various_keys(self):
        for k in ["C", "G", "F", "Bb", "E", "Ab"]:
            song = generate_canon(voices=3, key=k, seed=42)
            assert k in song.title

    def test_custom_delay(self):
        song = generate_canon(voices=3, key="C", delay_beats=8.0, seed=42)
        assert len(song.tracks) == 3

    def test_seed_reproducibility(self):
        s1 = generate_canon(voices=3, key="C", seed=99)
        s2 = generate_canon(voices=3, key="C", seed=99)
        assert s1.title == s2.title
        assert len(s1.tracks) == len(s2.tracks)
        for t1, t2 in zip(s1.tracks, s2.tracks):
            assert len(t1.beats) == len(t2.beats)

    def test_all_tracks_have_content(self):
        song = generate_canon(voices=4, key="G", seed=42)
        for track in song.tracks:
            assert len(track.beats) > 0, f"Track {track.name} is empty"

    def test_bpm_respected(self):
        song = generate_canon(voices=2, key="C", bpm=140, seed=42)
        assert song.bpm == 140

    def test_empty_melody_generates_one(self):
        """Empty or too-short melody triggers auto-generation."""
        song = generate_canon(melody=[], voices=3, key="C", seed=42)
        assert len(song.tracks) == 3
        # Should have content despite empty input
        for track in song.tracks:
            assert len(track.beats) > 0


# ---------------------------------------------------------------------------
# generate_sonata_form
# ---------------------------------------------------------------------------


class TestGenerateSonataForm:
    """Sonata-allegro form generator produces valid Songs."""

    def test_basic_sonata(self):
        song = generate_sonata_form(key="C", mode="major", seed=42)
        assert isinstance(song, Song)
        assert "Sonata" in song.title
        assert "C" in song.title
        assert "major" in song.title
        assert len(song.tracks) == 2  # melody + chords

    def test_minor_mode(self):
        song = generate_sonata_form(key="A", mode="minor", seed=42)
        assert "minor" in song.title

    def test_without_development(self):
        song_full = generate_sonata_form(key="C", include_development=True, seed=42)
        song_no_dev = generate_sonata_form(key="C", include_development=False, seed=42)
        # Full sonata should be longer than one without development
        full_beats = sum(len(t.beats) for t in song_full.tracks)
        no_dev_beats = sum(len(t.beats) for t in song_no_dev.tracks)
        assert full_beats > no_dev_beats

    def test_without_coda(self):
        song_coda = generate_sonata_form(key="C", include_coda=True, seed=42)
        song_no_coda = generate_sonata_form(key="C", include_coda=False, seed=42)
        full_beats = sum(len(t.beats) for t in song_coda.tracks)
        no_coda_beats = sum(len(t.beats) for t in song_no_coda.tracks)
        assert full_beats > no_coda_beats

    def test_various_keys(self):
        for k in ["C", "G", "D", "F", "Bb", "Eb"]:
            song = generate_sonata_form(key=k, seed=42)
            assert k in song.title

    def test_bpm_respected(self):
        song = generate_sonata_form(key="C", bpm=90, seed=42)
        assert song.bpm == 90

    def test_seed_reproducibility(self):
        s1 = generate_sonata_form(key="C", seed=123)
        s2 = generate_sonata_form(key="C", seed=123)
        assert s1.title == s2.title
        for t1, t2 in zip(s1.tracks, s2.tracks):
            assert len(t1.beats) == len(t2.beats)

    def test_all_tracks_have_content(self):
        song = generate_sonata_form(key="G", seed=42)
        for track in song.tracks:
            assert len(track.beats) > 0, f"Track {track.name} is empty"

    def test_melody_track_has_notes(self):
        song = generate_sonata_form(key="C", seed=42)
        melody_track = next(t for t in song.tracks if t.name == "melody")
        note_count = sum(
            1
            for b in melody_track.beats
            if b.event and isinstance(b.event, Note) and b.event.pitch is not None
        )
        assert note_count > 0, "Melody track should contain pitched notes"

    def test_minimal_sonata(self):
        """Sonata without development or coda is still valid."""
        song = generate_sonata_form(key="C", include_development=False, include_coda=False, seed=42)
        assert len(song.tracks) == 2
        for track in song.tracks:
            assert len(track.beats) > 0


# ---------------------------------------------------------------------------
# generate_rondo
# ---------------------------------------------------------------------------


class TestGenerateRondo:
    """Rondo form generator produces valid Songs."""

    def test_basic_rondo(self):
        song = generate_rondo(key="G", episodes=2, seed=42)
        assert isinstance(song, Song)
        assert "Rondo" in song.title
        assert "G" in song.title
        assert len(song.tracks) == 2  # melody + chords

    def test_episode_counts(self):
        for ep in [1, 2, 3, 4]:
            song = generate_rondo(key="C", episodes=ep, seed=42)
            assert len(song.tracks) == 2

    def test_more_episodes_means_longer_song(self):
        song_2 = generate_rondo(key="C", episodes=2, seed=42)
        song_4 = generate_rondo(key="C", episodes=4, seed=42)
        beats_2 = sum(len(t.beats) for t in song_2.tracks)
        beats_4 = sum(len(t.beats) for t in song_4.tracks)
        assert beats_4 > beats_2

    def test_episodes_clamped_low(self):
        """Episodes below 1 are clamped."""
        song = generate_rondo(key="C", episodes=0, seed=42)
        assert len(song.tracks) == 2
        for track in song.tracks:
            assert len(track.beats) > 0

    def test_episodes_clamped_high(self):
        """Episodes above 4 are clamped."""
        song = generate_rondo(key="C", episodes=10, seed=42)
        assert len(song.tracks) == 2

    def test_various_keys(self):
        for k in ["C", "D", "F", "A", "Eb", "B"]:
            song = generate_rondo(key=k, seed=42)
            assert k in song.title

    def test_bpm_respected(self):
        song = generate_rondo(key="C", bpm=160, seed=42)
        assert song.bpm == 160

    def test_seed_reproducibility(self):
        s1 = generate_rondo(key="C", episodes=2, seed=55)
        s2 = generate_rondo(key="C", episodes=2, seed=55)
        assert s1.title == s2.title
        for t1, t2 in zip(s1.tracks, s2.tracks):
            assert len(t1.beats) == len(t2.beats)

    def test_all_tracks_have_content(self):
        song = generate_rondo(key="F", episodes=3, seed=42)
        for track in song.tracks:
            assert len(track.beats) > 0, f"Track {track.name} is empty"

    def test_melody_has_notes(self):
        song = generate_rondo(key="C", seed=42)
        melody_track = next(t for t in song.tracks if t.name == "melody")
        note_count = sum(
            1
            for b in melody_track.beats
            if b.event and isinstance(b.event, Note) and b.event.pitch is not None
        )
        assert note_count > 0

    def test_different_scale(self):
        song = generate_rondo(key="A", scale_name="aeolian", episodes=2, seed=42)
        assert "Rondo" in song.title
        assert len(song.tracks) == 2


# ---------------------------------------------------------------------------
# Cross-form integration tests
# ---------------------------------------------------------------------------


class TestFormGeneratorIntegration:
    """Integration tests across all form generators."""

    def test_all_forms_return_song(self):
        """Every form generator returns a Song object."""
        canon = generate_canon(voices=2, key="C", seed=42)
        sonata = generate_sonata_form(key="C", seed=42)
        rondo = generate_rondo(key="C", seed=42)

        assert isinstance(canon, Song)
        assert isinstance(sonata, Song)
        assert isinstance(rondo, Song)

    def test_all_forms_have_titles(self):
        canon = generate_canon(voices=2, key="D", seed=42)
        sonata = generate_sonata_form(key="D", seed=42)
        rondo = generate_rondo(key="D", seed=42)

        assert "D" in canon.title
        assert "D" in sonata.title
        assert "D" in rondo.title

    def test_all_forms_produce_notes(self):
        """Every form produces at least some pitched notes."""
        forms = [
            generate_canon(voices=3, key="C", seed=42),
            generate_sonata_form(key="C", seed=42),
            generate_rondo(key="C", seed=42),
        ]
        for song in forms:
            total_notes = 0
            for track in song.tracks:
                for beat in track.beats:
                    if beat.event and isinstance(beat.event, Note) and beat.event.pitch is not None:
                        total_notes += 1
            assert total_notes > 0, f"{song.title} should contain notes"

    def test_imports_from_top_level(self):
        """All generators importable from code_music directly."""
        from code_music import generate_canon, generate_sonata_form, generate_rondo

        assert callable(generate_canon)
        assert callable(generate_sonata_form)
        assert callable(generate_rondo)

    def test_imports_from_theory(self):
        """All generators importable from code_music.theory."""
        from code_music.theory import generate_canon, generate_sonata_form, generate_rondo

        assert callable(generate_canon)
        assert callable(generate_sonata_form)
        assert callable(generate_rondo)
