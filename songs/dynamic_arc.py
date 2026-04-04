"""Dynamic Arc — crescendo to sforzando to decrescendo with rubato."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import rubato, sforzando
from code_music import crescendo, decrescendo

song = Song(title="Dynamic Arc", bpm=72)

# Build a melody
raw = [
    Note("C", 5, 1.0),
    Note("D", 5, 1.0),
    Note("E", 5, 1.0),
    Note("F", 5, 1.0),
    Note("G", 5, 1.0),
    Note("A", 5, 1.0),
    Note("B", 5, 1.0),
    Note("C", 6, 1.0),
    Note("B", 5, 1.0),
    Note("A", 5, 1.0),
    Note("G", 5, 1.0),
    Note("F", 5, 1.0),
    Note("E", 5, 1.0),
    Note("D", 5, 1.0),
    Note("C", 5, 1.0),
    Note("C", 5, 2.0),
]

# Crescendo first half, decrescendo second half
first_half = crescendo(raw[:8], start_vel=30, end_vel=100)
# Sforzando on the peak
first_half = sforzando(first_half, position=7, accent_vel=127)
second_half = decrescendo(raw[8:], start_vel=100, end_vel=30)
full = first_half + second_half

# Apply rubato
full = rubato(full, amount=0.12, seed=42)

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.1))
lead.extend(full)

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3))
pad.add(Chord("C", "maj", 3, duration=16.0))

song.effects = {
    "lead": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
}
