"""Roman Numeral Pop — the I-V-vi-IV progression written in analysis notation."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import progression_from_roman

song = Song(title="Roman Numeral Pop", bpm=120)

# The most popular chord progression in modern pop, written in Roman numerals
pop_prog = progression_from_roman(["I", "V", "vi", "IV"], "G")

# Repeat 4 times
chords_track = song.add_track(Track(name="chords", instrument="piano", volume=0.45, pan=-0.1))
for _ in range(4):
    for root, shape in pop_prog:
        chords_track.add(Chord(root, shape, 3, duration=4.0))

# Bass from the progression
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for _ in range(4):
    for root, _ in pop_prog:
        bass.add(Note(root, 2, 2.0))
        bass.add(Note(root, 2, 2.0))

# Catchy melody
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=0.2))
melody = [
    Note("B", 5, 1.0),
    Note("D", 6, 0.5),
    Note("B", 5, 0.5),
    Note("A", 5, 2.0),
    Note("D", 6, 1.0),
    Note("B", 5, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 2.0),
    Note("E", 5, 1.0),
    Note("G", 5, 0.5),
    Note("A", 5, 0.5),
    Note("B", 5, 2.0),
    Note("C", 6, 1.0),
    Note("B", 5, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 2.0),
]
for _ in range(4):
    lead.extend(melody)

song.effects = {
    "chords": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
    "lead": EffectsChain().add(delay, delay_ms=250, feedback=0.2, wet=0.15),
}
