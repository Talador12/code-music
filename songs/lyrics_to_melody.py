"""Lyrics to Melody — text mapped to notes via syllable stress."""

from code_music import Chord, EffectsChain, Song, Track, delay, reverb
from code_music.theory import text_to_melody

song = Song(title="Lyrics to Melody", bpm=100)

lines = [
    "the stars are falling down tonight",
    "and all the world is sleeping tight",
    "but I am wide awake and dreaming",
    "of a place where light is streaming",
]

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.1))
for i, line in enumerate(lines):
    notes = text_to_melody(line, key="A", scale_name="minor", octave=5, seed=i)
    lead.extend(notes)

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35, pan=-0.15))
pad.add(Chord("A", "min7", 3, duration=16.0))
pad.add(Chord("F", "maj7", 3, duration=16.0))

song.effects = {
    "lead": EffectsChain().add(delay, delay_ms=300, feedback=0.2, wet=0.15),
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
}
