"""Persian Night - exotic Persian scale with atmospheric pad."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale

song = Song(title="Persian Night", bpm=76, sample_rate=44100)

lead = song.add_track(Track(name="lead", instrument="triangle", volume=0.45, pan=0.15))
lead.extend(scale("D", "persian", octave=5, length=14))

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3))
for root, shape in [("D", "min"), ("Eb", "maj"), ("A", "dom7"), ("D", "min")] * 2:
    pad.add(Chord(root, shape, 3, duration=4.0, velocity=35))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.4))
for root in ["D", "Eb", "A", "D"] * 2:
    bass.add(Note(root, 2, 4.0, velocity=50))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.85, wet=0.4),
}
