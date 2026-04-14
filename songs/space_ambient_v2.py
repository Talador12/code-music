"""Space Ambient v2 - evolving pads with room reverb and spatial orbiting."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.effects import orbit, room_reverb

song = Song(title="Space Ambient v2", bpm=50, sample_rate=44100)

# Deep pad
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3))
for root, shape in [("E", "min7"), ("C", "maj7"), ("G", "maj"), ("D", "min7")]:
    pad.add(Chord(root, shape, 3, duration=16.0, velocity=30))

# Orbiting shimmer
shimmer = song.add_track(Track(name="shimmer", instrument="sine", volume=0.15, pan=0.3))
for note in ["B", "E", "G", "B"] * 4:
    shimmer.add(Note(note, 6, 4.0, velocity=20))

# Sub drone
sub = song.add_track(Track(name="sub", instrument="bass", volume=0.3))
sub.add(Note("E", 1, 64.0, velocity=40))

song.effects = {
    "pad": EffectsChain()
    .add(room_reverb, width=20, depth=30, height=10, absorption=0.15, wet=0.4)
    .add(reverb, room_size=0.95, wet=0.5),
    "shimmer": lambda samples, sr: orbit(samples, sr, rate=0.15, radius=3.0),
}
