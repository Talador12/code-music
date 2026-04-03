"""Tests for utility functions: humanize, transpose, detect_tempo."""

import numpy as np

from code_music import Note, Song, Track
from code_music.theory import detect_tempo, humanize_velocity, transpose_progression

SR = 22050


class TestHumanizeVelocity:
    def test_basic(self):
        notes = [Note("C", 5, 1.0, velocity=0.8) for _ in range(8)]
        h = humanize_velocity(notes, amount=0.15, seed=42)
        assert len(h) == 8
        vels = [n.velocity for n in h]
        assert not all(v == 0.8 for v in vels)

    def test_rests_preserved(self):
        notes = [Note.rest(1.0)]
        h = humanize_velocity(notes, seed=42)
        assert h[0].pitch is None

    def test_velocity_bounds(self):
        notes = [Note("C", 5, 1.0, velocity=0.05) for _ in range(20)]
        h = humanize_velocity(notes, amount=0.5, seed=42)
        assert all(0.05 <= n.velocity <= 1.0 for n in h)

    def test_reproducible(self):
        notes = [Note("C", 5, 1.0) for _ in range(4)]
        a = humanize_velocity(notes, seed=42)
        b = humanize_velocity(notes, seed=42)
        assert [n.velocity for n in a] == [n.velocity for n in b]


class TestTransposeProgression:
    def test_up_semitone(self):
        prog = [("C", "maj"), ("G", "dom7")]
        t = transpose_progression(prog, semitones=1)
        assert t[0] == ("C#", "maj")

    def test_down_semitone(self):
        prog = [("C", "maj")]
        t = transpose_progression(prog, semitones=-1)
        assert t[0] == ("B", "maj")

    def test_preserves_shape(self):
        prog = [("D", "min7")]
        t = transpose_progression(prog, semitones=5)
        assert t[0][1] == "min7"

    def test_octave_wrap(self):
        prog = [("A", "maj")]
        t = transpose_progression(prog, semitones=12)
        assert t[0] == ("A", "maj")


class TestDetectTempo:
    def test_returns_float(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8)).extend(
            [Note("C", 2, 1.0) for _ in range(16)]
        )
        audio = song.render()
        bpm = detect_tempo(audio, SR)
        assert isinstance(bpm, float)
        assert 60 <= bpm <= 200

    def test_short_audio(self):
        bpm = detect_tempo(np.zeros(100), SR)
        assert bpm == 120.0  # fallback
