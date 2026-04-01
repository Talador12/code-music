"""Tests for v5.0: Song.generate, detect_key, CLI --random."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np

from code_music.engine import (
    Chord,
    Note,
    Song,
    Track,
    detect_key,
    generate_song,
)

ROOT = Path(__file__).resolve().parents[1]


class TestGenerateSong:
    def test_generates_valid_song(self):
        song = generate_song("lo_fi", bars=8, seed=42)
        assert isinstance(song, Song)
        assert len(song.tracks) > 0
        assert song.bpm > 0

    def test_all_genres_work(self):
        for genre in ["lo_fi", "jazz", "ambient", "edm", "rock", "classical", "funk", "hip_hop"]:
            song = generate_song(genre, bars=4, seed=99)
            assert len(song.tracks) >= 2, f"{genre} should have at least 2 tracks"

    def test_seed_produces_deterministic_output(self):
        s1 = generate_song("jazz", bars=4, seed=42)
        s2 = generate_song("jazz", bars=4, seed=42)
        assert len(s1.tracks) == len(s2.tracks)
        for t1, t2 in zip(s1.tracks, s2.tracks):
            assert len(t1.beats) == len(t2.beats)

    def test_different_seeds_produce_different_output(self):
        s1 = generate_song("edm", bars=8, seed=1)
        s2 = generate_song("edm", bars=8, seed=2)
        # At least one track should differ in note content
        any_different = False
        for t1, t2 in zip(s1.tracks, s2.tracks):
            if t1.name == "lead":
                for b1, b2 in zip(t1.beats, t2.beats):
                    if b1.event and b2.event:
                        if getattr(b1.event, "pitch", None) != getattr(b2.event, "pitch", None):
                            any_different = True
                            break
        assert any_different

    def test_renders_without_error(self):
        song = generate_song("rock", bars=4, seed=42, sample_rate=22050)
        audio = song.render()
        assert audio.shape[0] > 0
        assert np.max(np.abs(audio)) > 0.0

    def test_unknown_genre_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Unknown genre"):
            generate_song("grindcore")

    def test_custom_title(self):
        song = generate_song("ambient", bars=4, seed=1, title="My Ambient")
        assert song.title == "My Ambient"


class TestDetectKey:
    def test_detects_c_major(self):
        song = Song(bpm=120)
        tr = song.add_track(Track(instrument="piano"))
        for note in ["C", "D", "E", "F", "G", "A", "B"]:
            tr.add(Note(note, 4, 1.0))
        root, mode, conf = detect_key(song)
        assert root == "C"
        assert mode == "major"
        assert conf > 0.5

    def test_detects_a_minor_or_c_major(self):
        # A natural minor = C major relative — both are valid detections
        song = Song(bpm=120)
        tr = song.add_track(Track(instrument="piano"))
        for note in ["A", "B", "C", "D", "E", "F", "G"]:
            tr.add(Note(note, 4, 1.0))
        root, mode, conf = detect_key(song)
        assert (root, mode) in [("A", "minor"), ("C", "major")]
        assert conf > 0.3

    def test_detects_key_from_chords(self):
        song = Song(bpm=120)
        tr = song.add_track(Track(instrument="pad"))
        tr.add(Chord("G", "maj", 3, duration=4.0))
        tr.add(Chord("C", "maj", 3, duration=4.0))
        tr.add(Chord("D", "maj", 3, duration=4.0))
        tr.add(Chord("G", "maj", 3, duration=4.0))
        root, mode, conf = detect_key(song)
        assert root == "G"
        assert conf > 0.3

    def test_empty_song_returns_c_major_zero_confidence(self):
        song = Song(bpm=120)
        root, mode, conf = detect_key(song)
        assert root == "C"
        assert mode == "major"
        assert conf == 0.0

    def test_returns_tuple_of_three(self):
        song = Song(bpm=120)
        tr = song.add_track(Track(instrument="sine"))
        tr.add(Note("E", 4, 4.0))
        result = detect_key(song)
        assert len(result) == 3
        root, mode, conf = result
        assert isinstance(root, str)
        assert mode in ("major", "minor")
        assert 0.0 <= conf <= 1.0

    def test_detect_key_on_generated_song(self):
        song = generate_song("jazz", bars=8, seed=42)
        root, mode, conf = detect_key(song)
        # Jazz template uses D dorian, so D should be detected
        assert conf > 0.3  # Should have reasonable confidence


class TestCLIRandom:
    def test_random_unknown_genre_fails(self):
        result = subprocess.run(
            [sys.executable, "-m", "code_music.cli", "--random", "polka_metal"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            timeout=10,
        )
        assert result.returncode != 0
        assert "unknown genre" in result.stderr.lower()

    def test_generate_song_used_by_random_is_valid(self):
        # Test the generation path without subprocess play (which times out)
        song = generate_song("ambient", bars=4, seed=42, sample_rate=22050)
        assert len(song.tracks) >= 2
        assert song.bpm > 0
        audio = song.render()
        assert audio.shape[0] > 0
