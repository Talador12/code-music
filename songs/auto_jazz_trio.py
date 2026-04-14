"""Auto Jazz Trio - auto_accompany builds a jazz trio from a melody."""

from code_music import Note
from code_music.theory import auto_accompany

# ii-V-I melody in Bb
melody = [
    Note("C", 5, 0.5),
    Note("D", 5, 0.5),
    Note("Eb", 5, 0.5),
    Note("F", 5, 0.5),
    Note("G", 5, 1.0),
    Note("F", 5, 0.5),
    Note("Eb", 5, 0.5),
    Note("D", 5, 1.0),
    Note("C", 5, 0.5),
    Note("Bb", 4, 0.5),
    Note("A", 4, 1.0),
    Note("Bb", 4, 2.0),
    Note("D", 5, 0.5),
    Note("F", 5, 0.5),
    Note("G", 5, 1.0),
    Note("A", 5, 0.5),
    Note("Bb", 5, 0.5),
    Note("A", 5, 1.0),
    Note("G", 5, 0.5),
    Note("F", 5, 0.5),
    Note("Eb", 5, 1.0),
    Note("D", 5, 1.0),
    Note("Bb", 4, 2.0),
]

song = auto_accompany(melody, key="Bb", genre="jazz", bpm=160, title="Auto Jazz Trio", seed=1959)
