"""Gate effect showcase: pad with square/ramp/trapezoid gate shapes."""

from code_music import Chord, Song, Track, gate, reverb

song = Song(title="gate_effects", bpm=128)
for shape, pan_v in [("square", -0.4), ("ramp_up", 0.0), ("trapezoid", 0.4)]:
    tr = song.add_track(Track(name=shape, instrument="strings", volume=0.6, pan=pan_v))
    for _ in range(4):
        tr.add(Chord("A", "min7", 3, duration=4.0, velocity=0.65))
song._effects = {
    "square": lambda s, sr: gate(s, sr, rate_hz=4.0, shape="square"),
    "ramp_up": lambda s, sr: gate(s, sr, rate_hz=4.0, shape="ramp_up"),
    "trapezoid": lambda s, sr: gate(reverb(s, sr, wet=0.2), sr, rate_hz=4.0, shape="trapezoid"),
}
