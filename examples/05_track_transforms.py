"""05 — Track transforms: transpose, loop, split, merge, stretch, filter.

Run:  code-music examples/05_track_transforms.py --play
"""

import random

from code_music import EffectsChain, Note, Song, Track, delay, reverb

song = Song(title="Track Transforms", bpm=110)

r = Note.rest

# Start with a simple 2-bar riff
riff = Track(name="riff", instrument="piano", volume=0.5)
riff.extend(
    [
        Note("C", 4, 0.5),
        Note("E", 4, 0.5),
        Note("G", 4, 0.5),
        Note("C", 5, 0.5),
        Note("B", 4, 1.0),
        Note("G", 4, 1.0),
        Note("A", 4, 0.5),
        Note("F", 4, 0.5),
        Note("D", 4, 1.0),
        Note("C", 4, 2.0),
    ]
)

# LOOP: repeat the riff 4 times
looped = riff.loop(4)

# TRANSPOSE: shift up a perfect fifth for harmony
harmony = riff.transpose(7).loop(4)
harmony.name = "harmony"
harmony.pan = 0.3
harmony.volume = 0.4

# SPLIT: cut the looped riff at bar 4 (beat 16)
first_half, second_half = looped.split(at_beat=16.0)

# STRETCH: slow down the second half
slow_ending = second_half.stretch(2.0).fade_out(beats=16.0)

# CONCAT: join first half + slow ending
song.add_track(first_half.concat(slow_ending))
song.add_track(harmony)

# FILTER: keep only loud notes from the riff (velocity > 0.5)
# (all default to 0.8, so this keeps everything — for demo purposes,
#  let's create a varied-velocity track first)
varied = Track(name="accent", instrument="pluck", volume=0.4, pan=-0.2)
rng = random.Random(99)
for _ in range(32):
    v = rng.choice([0.3, 0.5, 0.7, 0.9])
    varied.add(Note("C", 5, 0.5, velocity=v))
# Filter: only the loud hits come through, rests fill the gaps
accents = varied.filter(lambda e: e.velocity > 0.6)
song.add_track(accents)

# MERGE: overlay a ride pattern onto the accent gaps
ride = Track(name="accent", instrument="drums_hat", volume=0.25)
for _ in range(32):
    ride.add(Note.rest(0.5) if rng.random() > 0.3 else Note("F#", 6, 0.5, velocity=0.3))
song.add_track(accents.merge(ride))

# Bass anchor
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55))
for _ in range(12):
    bass.extend([Note("C", 2, 2.0), Note("G", 2, 2.0)])

song.effects = {
    "riff": EffectsChain().add(reverb, room_size=0.4, wet=0.15),
    "harmony": EffectsChain().add(delay, delay_ms=250, feedback=0.2, wet=0.15),
}
