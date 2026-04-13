"""Pitch Class Analysis — frequency of each note in a melody."""

from code_music import Note, Song, Track
from code_music.theory import count_pitch_classes, melodic_interval_histogram

melody = [
    Note(n, 5, 0.5)
    for n in ["C", "E", "G", "C", "E", "G", "B", "C", "D", "E", "F", "G", "A", "B", "C", "C"]
]
print(f"Pitch classes: {count_pitch_classes(melody)}")
print(f"Intervals: {melodic_interval_histogram(melody)}")
song = Song(title="Pitch Class Analysis", bpm=120, sample_rate=44100)
song.add_track(Track(name="lead", instrument="piano", volume=0.5)).extend(melody)
song.effects = {}
