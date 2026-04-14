"""ambient_space.py - Slow ambient with long reverb tails. Floating in orbit."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb

song = Song(title="Ambient Space", bpm=50, sample_rate=44100)

# Deep pad - long sustained chords
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35, pan=-0.1))
for root, shape in [("E", "min9"), ("C", "maj7"), ("G", "maj7"), ("D", "min7")] * 2:
    pad.add(Chord(root, shape, 3, duration=16.0, velocity=35))

# High shimmer - sparse melody notes with lots of space
shimmer = song.add_track(Track(name="shimmer", instrument="triangle", volume=0.25, pan=0.3))
phrase = [
    Note("B", 5, 2.0),
    Note.rest(4.0),
    Note("E", 6, 3.0),
    Note.rest(3.0),
    Note("G", 5, 2.0),
    Note.rest(2.0),
]
shimmer.extend(phrase * 8)

# Sub bass - barely there
sub = song.add_track(Track(name="sub", instrument="bass", volume=0.3))
for root in ["E", "C", "G", "D"] * 2:
    sub.add(Note(root, 1, 16.0, velocity=40))

# Second texture layer
air = song.add_track(Track(name="air", instrument="sine", volume=0.15, pan=0.2))
tones = [Note("E", 4, 8.0), Note.rest(8.0), Note("G", 4, 8.0), Note.rest(8.0)]
air.extend(tones * 4)

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.95, wet=0.6),
    "shimmer": EffectsChain()
    .add(delay, delay_ms=1500.0, feedback=0.5, wet=0.4)
    .add(reverb, room_size=0.9, wet=0.5),
    "air": EffectsChain().add(reverb, room_size=0.85, wet=0.45),
}
