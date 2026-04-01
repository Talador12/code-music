"""ragtime_rag.py — Ragtime. C major, 120 BPM. Scott Joplin stride piano.

A bouncy ragtime piece with striding left hand, syncopated right-hand melody,
and a classic AABB form using Section.repeat.

Style: Ragtime, C major, 120 BPM.
"""

from code_music import Chord, EffectsChain, Note, Section, Song, reverb

song = Song(title="Ragtime Rag", bpm=120)
r = Note.rest

section_a = Section("A", bars=4)
section_a.add_track("left_hand", [
    Note("C", 2, 1.0), Chord("C", "maj", 3, duration=1.0),
    Note("G", 2, 1.0), Chord("C", "maj", 3, duration=1.0),
    Note("F", 2, 1.0), Chord("F", "maj", 3, duration=1.0),
    Note("C", 2, 1.0), Chord("C", "maj", 3, duration=1.0),
    Note("G", 2, 1.0), Chord("G", "maj", 3, duration=1.0),
    Note("C", 2, 1.0), Chord("C", "maj", 3, duration=1.0),
    Note("F", 2, 1.0), Chord("F", "maj", 3, duration=1.0),
    Note("G", 2, 1.0), Chord("G", "dom7", 3, duration=1.0),
])
section_a.add_track("right_hand", [
    Note("E", 5, 0.5), Note("C", 5, 0.5), Note("D", 5, 0.5), Note("E", 5, 0.5),
    Note("G", 5, 1.0), Note("E", 5, 1.0),
    Note("A", 5, 0.5), Note("G", 5, 0.5), Note("F", 5, 0.5), Note("E", 5, 0.5),
    Note("D", 5, 1.0), Note("C", 5, 1.0),
    Note("E", 5, 0.5), Note("D", 5, 0.5), Note("C", 5, 0.5), Note("B", 4, 0.5),
    Note("C", 5, 1.0), Note("E", 5, 1.0),
    Note("D", 5, 0.5), Note("C", 5, 0.5), Note("B", 4, 1.0),
    Note("C", 5, 2.0),
])

section_b = Section("B", bars=4)
section_b.add_track("left_hand", [
    Note("F", 2, 1.0), Chord("F", "maj", 3, duration=1.0),
    Note("C", 2, 1.0), Chord("C", "maj", 3, duration=1.0),
    Note("D", 2, 1.0), Chord("D", "min", 3, duration=1.0),
    Note("G", 2, 1.0), Chord("G", "dom7", 3, duration=1.0),
    Note("C", 2, 1.0), Chord("C", "maj", 3, duration=1.0),
    Note("A", 2, 1.0), Chord("A", "min", 3, duration=1.0),
    Note("F", 2, 1.0), Chord("F", "maj", 3, duration=1.0),
    Note("G", 2, 1.0), Chord("G", "dom7", 3, duration=1.0),
])
section_b.add_track("right_hand", [
    Note("A", 5, 0.5), Note("G", 5, 0.5), Note("F", 5, 0.5), Note("E", 5, 0.5),
    Note("F", 5, 1.0), Note("A", 5, 1.0),
    Note("G", 5, 0.5), Note("F", 5, 0.5), Note("E", 5, 0.5), Note("D", 5, 0.5),
    Note("E", 5, 1.0), Note("G", 5, 1.0),
    Note("C", 6, 0.5), Note("B", 5, 0.5), Note("A", 5, 0.5), Note("G", 5, 0.5),
    Note("A", 5, 1.0), Note("F", 5, 1.0),
    Note("E", 5, 0.5), Note("D", 5, 0.5), Note("C", 5, 1.0),
    Note("C", 5, 2.0),
])

song.arrange(
    [*section_a.repeat(2), *section_b.repeat(2), *section_a.repeat(2), *section_b.repeat(2)],
    instruments={"left_hand": "piano", "right_hand": "piano"},
    volumes={"left_hand": 0.5, "right_hand": 0.55},
    pans={"left_hand": -0.15, "right_hand": 0.15},
)

song.effects = {
    "right_hand": EffectsChain().add(reverb, room_size=0.4, wet=0.15),
    "left_hand": EffectsChain().add(reverb, room_size=0.35, wet=0.12),
}
