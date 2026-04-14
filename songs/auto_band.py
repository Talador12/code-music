"""Auto Band - melody in, full arrangement out via auto_accompany."""

from code_music import Note
from code_music.theory import auto_accompany

# Write a melody by hand
melody = [
    Note("E", 5, 1.0),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("D", 5, 1.0),
    Note("E", 5, 1.0),
    Note("E", 5, 1.0),
    Note("E", 5, 1.0),
    Note("D", 5, 1.0),
    Note("D", 5, 1.0),
    Note("D", 5, 2.0),
    Note("E", 5, 1.0),
    Note("G", 5, 1.0),
    Note("G", 5, 2.0),
    Note("E", 5, 1.0),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("D", 5, 1.0),
    Note("E", 5, 1.0),
    Note("E", 5, 1.0),
    Note("E", 5, 1.0),
    Note("D", 5, 1.0),
    Note("D", 5, 1.0),
    Note("E", 5, 1.0),
    Note("D", 5, 1.0),
    Note("C", 5, 4.0),
]

# auto_accompany builds chords, bass, and drums around it
song = auto_accompany(
    melody,
    key="C",
    genre="pop",
    bpm=120,
    title="Auto Band",
    seed=42,
)
