"""desert_blues.py - Saharan desert blues. E pentatonic, 105 BPM.

Hypnotic pentatonic riff over a steady pulse. Tinariwen-style
repetitive guitar with a deep, anchoring bass drone.

Style: Desert blues, E pentatonic, 105 BPM.
"""

from code_music import EffectsChain, Note, Song, Track, delay, reverb, scale

song = Song(title="Desert Blues", bpm=105, sample_rate=44100)
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.65))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3))
for _ in range(20):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    hat.extend([Note("F#", 6, 0.5)] * 8)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
for _ in range(20):
    bass.extend([Note("E", 2, 2.0), Note("E", 2, 1.0), Note("B", 1, 1.0)])

guitar = song.add_track(Track(name="guitar", instrument="pluck", volume=0.5, pan=0.15))
pent = scale("E", "pentatonic", octave=4, length=5)
riff = [pent[0], pent[2], pent[4], pent[2], pent[1], pent[0]]
for _ in range(20):
    for n in riff:
        guitar.add(Note(n.pitch, n.octave, 0.5))
    guitar.add(r(1.0))

guitar2 = song.add_track(Track(name="guitar2", instrument="pluck", volume=0.35, pan=-0.2))
for _ in range(10):
    guitar2.extend(
        [
            Note("E", 5, 2.0),
            Note("B", 4, 1.0),
            Note("A", 4, 1.0),
            Note("E", 5, 1.0),
            Note("G#", 4, 1.0),
            r(2.0),
        ]
    )

song.effects = {
    "guitar": EffectsChain()
    .add(delay, delay_ms=285, feedback=0.2, wet=0.15)
    .add(reverb, room_size=0.5, wet=0.2),
    "guitar2": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
}
