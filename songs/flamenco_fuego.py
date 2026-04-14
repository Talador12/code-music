"""flamenco_fuego.py - Flamenco. E Phrygian dominant, 95 BPM.

Slow-burning flamenco with Phrygian dominant scale, palmas claps,
and tremolo guitar over a cajon pulse. Duende in code form.

Style: Flamenco, E Phrygian dominant, 95 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale

song = Song(title="Flamenco Fuego", bpm=95, sample_rate=44100)
r = Note.rest

cajon = song.add_track(Track(name="cajon", instrument="drums_kick", volume=0.7))
palmas = song.add_track(Track(name="palmas", instrument="drums_hat", volume=0.35))
for _ in range(16):
    cajon.extend([Note("C", 2, 1.5), r(0.5), Note("C", 2, 0.5), Note("C", 2, 0.5), r(1.0)])
    palmas.extend(
        [
            r(0.5),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25),
            r(0.5),
            Note("F#", 6, 0.25),
            r(0.25),
            Note("F#", 6, 0.25),
            r(0.5),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25),
            r(0.75),
        ]
    )

guitar = song.add_track(Track(name="guitar", instrument="pluck", volume=0.5, pan=0.1))
phrygian = scale("E", "phrygian_dominant", octave=4, length=7)
for _ in range(8):
    for n in phrygian:
        guitar.add(Note(n.pitch, n.octave, 0.25))
    for n in reversed(phrygian):
        guitar.add(Note(n.pitch, n.octave, 0.25))
    guitar.add(r(0.5))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55))
for _ in range(16):
    bass.extend([Note("E", 2, 2.0), Note("F", 2, 1.0), Note("E", 2, 1.0)])

chords = song.add_track(Track(name="chords", instrument="pad", volume=0.2, pan=-0.1))
for _ in range(8):
    chords.extend([Chord("E", "min", 3, duration=4.0), Chord("F", "maj", 3, duration=4.0)])

song.effects = {
    "guitar": EffectsChain().add(reverb, room_size=0.45, wet=0.2),
    "chords": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
}
