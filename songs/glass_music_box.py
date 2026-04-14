"""Glass Music Box - crystalline wavetable tones with shaker rhythm."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb, scale
from code_music.sound_design import shaker, wt_glass

song = Song(title="Glass Music Box", bpm=88, sample_rate=44100)
song.register_instrument("wt_glass", wt_glass)
song.register_instrument("shaker", shaker)

# Glass melody
glass = song.add_track(Track(name="glass", instrument="wt_glass", volume=0.5, pan=0.1))
glass.extend(scale("A", "pentatonic", octave=5, length=16))

# Pad bed
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.25, pan=-0.15))
for root, shape in [("A", "min7"), ("D", "min7"), ("G", "maj7"), ("A", "min")] * 2:
    pad.add(Chord(root, shape, 3, duration=4.0, velocity=35))

# Shaker rhythm
sh = song.add_track(Track(name="shaker", instrument="shaker", volume=0.2))
for _ in range(32):
    sh.add(Note("C", 6, 0.5, velocity=30))

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.4))
for root in ["A", "D", "G", "A"] * 2:
    bass.add(Note(root, 2, 2.0, velocity=55))

song.effects = {
    "glass": EffectsChain()
    .add(delay, delay_ms=250, feedback=0.3, wet=0.2)
    .add(reverb, room_size=0.7, wet=0.3),
}
