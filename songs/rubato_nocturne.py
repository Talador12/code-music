"""Rubato Nocturne — Chopin-style push-pull timing over a simple progression."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import ritardando, rubato

song = Song(title="Rubato Nocturne", bpm=66)

melody = [
    Note("E", 5, 1.0),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("D", 5, 1.0),
    Note("E", 5, 1.0),
    Note("F", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A", 5, 2.0),
    Note("G", 5, 1.0),
    Note("F", 5, 0.5),
    Note("E", 5, 0.5),
    Note("D", 5, 1.0),
    Note("C", 5, 2.0),
]

# Apply rubato to the melody
rubato_melody = rubato(melody, amount=0.18, seed=42)

# Ritardando for the ending
ending = [Note("D", 5, 1.0), Note("C", 5, 2.0)]
slow_ending = ritardando(ending, start_bpm=66, end_bpm=40)

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.1))
lead.extend(rubato_melody)
lead.extend(slow_ending)

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=-0.1))
pad.add(Chord("C", "maj7", 3, duration=12.0))
pad.add(Chord("A", "min7", 3, duration=8.0))

song.effects = {
    "lead": EffectsChain().add(delay, delay_ms=400, feedback=0.2, wet=0.15),
    "pad": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
}
