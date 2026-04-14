"""baroque_prelude.py - Baroque prelude. C major, 66 BPM.

Bach-style figured bass with arpeggiated right hand over a walking
bass line. Counterpoint between two voices, harpsichord character.

Style: Baroque, C major, 66 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb

song = Song(title="Baroque Prelude", bpm=66, sample_rate=44100)
r = Note.rest

bass = song.add_track(Track(name="bass", instrument="pluck", volume=0.5))
bass_line = [
    Note("C", 3, 1.0),
    Note("D", 3, 1.0),
    Note("E", 3, 1.0),
    Note("C", 3, 1.0),
    Note("F", 3, 1.0),
    Note("E", 3, 1.0),
    Note("D", 3, 1.0),
    Note("G", 2, 1.0),
    Note("A", 2, 1.0),
    Note("B", 2, 1.0),
    Note("C", 3, 1.0),
    Note("E", 3, 1.0),
    Note("F", 3, 1.0),
    Note("D", 3, 1.0),
    Note("G", 2, 1.0),
    Note("C", 3, 1.0),
]
for _ in range(4):
    bass.extend(bass_line)

right = song.add_track(Track(name="right_hand", instrument="pluck", volume=0.45, pan=0.15))
arps = [
    [Note("E", 5, 0.25), Note("G", 5, 0.25), Note("C", 6, 0.25), Note("G", 5, 0.25)],
    [Note("F", 5, 0.25), Note("A", 5, 0.25), Note("D", 6, 0.25), Note("A", 5, 0.25)],
    [Note("E", 5, 0.25), Note("G", 5, 0.25), Note("B", 5, 0.25), Note("G", 5, 0.25)],
    [Note("F", 5, 0.25), Note("A", 5, 0.25), Note("C", 6, 0.25), Note("A", 5, 0.25)],
]
for _ in range(4):
    for arp in arps:
        right.extend(arp * 4)

chords = song.add_track(Track(name="chords", instrument="organ", volume=0.2))
progression = [
    Chord("C", "maj", 4, duration=4.0),
    Chord("D", "min", 4, duration=4.0),
    Chord("E", "min", 4, duration=4.0),
    Chord("F", "maj", 4, duration=4.0),
]
for _ in range(4):
    chords.extend(progression)

song.effects = {
    "right_hand": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
    "bass": EffectsChain().add(reverb, room_size=0.35, wet=0.15),
}
