"""Reich Phase — Steve Reich-style phasing between two identical patterns."""

from code_music import EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import phase_shift

song = Song(title="Reich Phase", bpm=130)

# The pattern — simple pentatonic loop
pattern = [
    Note("E", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A", 5, 0.5),
    Note("B", 5, 0.5),
    Note("D", 6, 0.5),
    Note("B", 5, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
]

# Phase: pattern B is displaced by 0.125 beats — drifts over repetitions
full_a = pattern * 8
full_b = pattern * 8
a, b = phase_shift(full_a, full_b, offset=0.125)

left = song.add_track(Track(name="left", instrument="piano", volume=0.5, pan=-0.4))
left.extend(a)

right = song.add_track(Track(name="right", instrument="piano", volume=0.5, pan=0.4))
right.extend(b)

song.effects = {
    "left": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
    "right": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
}
