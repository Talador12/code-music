"""Lydian Dreams - the dreamy raised-4th mode."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale

song = Song(title="Lydian Dreams", bpm=88, sample_rate=44100)

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.45, pan=0.15))
lead.extend(scale("C", "lydian", octave=5, length=16))

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=-0.1))
for root, shape in [("C", "maj7"), ("D", "maj"), ("E", "min7"), ("C", "maj7")] * 2:
    pad.add(Chord(root, shape, 3, duration=4.0, velocity=40))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.4))
for root in ["C", "D", "E", "C"] * 2:
    bass.add(Note(root, 2, 4.0, velocity=55))

song.effects = {
    "lead": EffectsChain().add(reverb, room_size=0.6, wet=0.25),
    "pad": EffectsChain().add(reverb, room_size=0.8, wet=0.35),
}
