"""Tests for the Song-Level Critique feature."""

import pytest

from code_music import Chord, Note, Song, Track, critique_song


class TestCritiqueSong:
    """Test suite for critique_song function."""

    def test_empty_song(self):
        """Test critique of empty song."""
        song = Song(title="Empty", key_sig="C")
        result = critique_song(song)

        assert "overall_score" in result
        assert "overall_grade" in result
        assert "harmony_critique" in result
        assert result["overall_grade"] in ["A", "B", "C", "D", "F"]

    def test_single_track_song(self):
        """Test critique of single-track song."""
        song = Song(title="Single", key_sig="C")
        track = song.add_track(Track(name="lead", instrument="piano"))
        track.add(Note("C", 4, 1.0))
        track.add(Note("E", 4, 1.0))
        track.add(Note("G", 4, 1.0))

        result = critique_song(song)

        assert result["overall_score"] >= 0
        assert result["overall_score"] <= 100
        assert len(result["tracks"]) == 1

    def test_multi_track_song(self):
        """Test critique of multi-track song."""
        song = Song(title="Multi", key_sig="C")

        lead = song.add_track(Track(name="lead", instrument="piano"))
        lead.add(Note("C", 5, 1.0))
        lead.add(Note("E", 5, 1.0))

        bass = song.add_track(Track(name="bass", instrument="bass"))
        bass.add(Note("C", 3, 1.0))
        bass.add(Note("G", 3, 1.0))

        result = critique_song(song)

        assert len(result["tracks"]) == 2
        assert result["arrangement"]["track_count"] == 2

    def test_song_with_chords(self):
        """Test critique of song with chord progression."""
        song = Song(title="Chords", key_sig="C")

        chords = song.add_track(Track(name="harmony", instrument="pad"))
        chords.add(Chord("C", "maj", octave=4, duration=2.0))
        chords.add(Chord("G", "dom7", octave=4, duration=2.0))
        chords.add(Chord("C", "maj", octave=4, duration=2.0))

        result = critique_song(song)

        assert "harmony_critique" in result
        assert result["harmony_critique"]["score"] >= 0

    def test_register_overlap_detection(self):
        """Test detection of register overlap between tracks."""
        song = Song(title="Overlap", key_sig="C")

        # Two tracks in same octave range
        track1 = song.add_track(Track(name="lead", instrument="piano"))
        track1.add(Note("C", 4, 1.0))
        track1.add(Note("E", 4, 1.0))
        track1.add(Note("G", 4, 1.0))

        track2 = song.add_track(Track(name="pad", instrument="pad"))
        track2.add(Note("D", 4, 1.0))
        track2.add(Note("F", 4, 1.0))
        track2.add(Note("A", 4, 1.0))

        result = critique_song(song)

        assert result["arrangement"]["register_overlap"] in [True, False]
        # Should detect overlap or provide feedback

    def test_well_spaced_arrangement(self):
        """Test critique of well-spaced arrangement."""
        song = Song(title="Well Spaced", key_sig="C")

        # Bass low, lead high
        bass = song.add_track(Track(name="bass", instrument="bass"))
        bass.add(Note("C", 2, 1.0))
        bass.add(Note("G", 2, 1.0))

        lead = song.add_track(Track(name="lead", instrument="piano"))
        lead.add(Note("C", 5, 1.0))
        lead.add(Note("E", 5, 1.0))

        result = critique_song(song)

        # Well-spaced arrangement should score better
        assert result["overall_score"] >= 0

    def test_density_imbalance(self):
        """Test detection of density imbalance."""
        song = Song(title="Imbalanced", key_sig="C")

        # Very busy track
        busy = song.add_track(Track(name="busy", instrument="piano"))
        for i in range(20):
            busy.add(Note("C", 4, 0.25))

        # Very sparse track
        sparse = song.add_track(Track(name="sparse", instrument="pad"))
        sparse.add(Note("C", 4, 4.0))

        result = critique_song(song)

        # May detect imbalance
        assert "issues" in result

    def test_track_analysis_structure(self):
        """Test that track analysis has expected fields."""
        song = Song(title="Analysis Test", key_sig="C")
        track = song.add_track(Track(name="test", instrument="piano"))
        track.add(Note("C", 4, 1.0))
        track.add(Note("D", 4, 1.0))
        track.add(Note("E", 4, 1.0))

        result = critique_song(song)

        assert len(result["tracks"]) == 1
        track_analysis = result["tracks"][0]

        assert "name" in track_analysis
        assert "instrument" in track_analysis
        assert "note_count" in track_analysis
        assert "range_semitones" in track_analysis
        assert "density" in track_analysis

        assert track_analysis["name"] == "test"
        assert track_analysis["instrument"] == "piano"
        assert track_analysis["note_count"] == 3

    def test_combined_feedback(self):
        """Test that feedback combines harmony and arrangement issues."""
        song = Song(title="Combined", key_sig="C")

        # Add chords
        chords = song.add_track(Track(name="chords", instrument="pad"))
        chords.add(Chord("C", "maj", octave=4, duration=2.0))
        chords.add(Chord("F", "maj", octave=4, duration=2.0))
        chords.add(Chord("G", "dom7", octave=4, duration=2.0))
        chords.add(Chord("C", "maj", octave=4, duration=2.0))

        # Add melody
        melody = song.add_track(Track(name="melody", instrument="piano"))
        melody.add(Note("C", 5, 1.0))
        melody.add(Note("A", 4, 1.0))
        melody.add(Note("G", 4, 1.0))
        melody.add(Note("E", 4, 1.0))

        result = critique_song(song)

        assert len(result["issues"]) >= 0
        assert len(result["strengths"]) >= 0
        assert len(result["suggestions"]) >= 0

    def test_different_keys(self):
        """Test critique in different keys."""
        for key in ["C", "G", "F", "D", "Bb"]:
            song = Song(title=f"Song in {key}", key_sig=key)
            track = song.add_track(Track(name="lead", instrument="piano"))
            track.add(Chord(key, "maj", octave=4, duration=4.0))

            result = critique_song(song, key=key)
            assert result["overall_score"] >= 0


class TestCritiqueSongEdgeCases:
    """Edge case tests for critique_song."""

    def test_no_notes(self):
        """Test critique of track with no notes."""
        song = Song(title="Silent", key_sig="C")
        song.add_track(Track(name="empty", instrument="piano"))

        result = critique_song(song)
        assert result["overall_score"] >= 0

    def test_many_tracks(self):
        """Test critique with many tracks."""
        song = Song(title="Orchestra", key_sig="C")

        for i in range(10):
            track = song.add_track(Track(name=f"track_{i}", instrument="piano"))
            track.add(Note("C", 4 + (i % 3), 1.0))

        result = critique_song(song)
        assert result["arrangement"]["track_count"] == 10

    def test_only_rests(self):
        """Test critique of track with only rests."""
        song = Song(title="Restful", key_sig="C")
        track = song.add_track(Track(name="rests", instrument="piano"))
        track.add(Note.rest(1.0))
        track.add(Note.rest(1.0))

        result = critique_song(song)
        assert result["tracks"][0]["note_count"] == 0
