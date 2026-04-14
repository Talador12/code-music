"""afrobeat_lagos.py - Afrobeat. Gm, 115 BPM. Lagos at midnight.

Polyrhythmic Fela-style groove with driving bass, horn stabs,
and interlocking percussion. Tony Allen's ghost in the machine.

Style: Afrobeat, Gm, 115 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, compress, reverb

song = Song(title="Afrobeat Lagos", bpm=115, sample_rate=44100)
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.75))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.4))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3))
for _ in range(20):
    kick.extend([Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5), r(0.5), Note("C", 2, 0.5), r(1.0)])
    snare.extend(
        [
            r(0.75),
            Note("E", 4, 0.25),
            r(1.0),
            Note("E", 4, 0.25),
            r(0.75),
            Note("E", 4, 0.25),
            r(0.75),
        ]
    )
    hat.extend([Note("F#", 6, 0.25)] * 16)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
riff = [
    Note("G", 2, 0.5),
    r(0.25),
    Note("G", 2, 0.25),
    Note("Bb", 2, 0.5),
    Note("C", 3, 0.5),
    Note("Bb", 2, 0.5),
    Note("G", 2, 0.5),
    Note("D", 3, 0.5),
]
for _ in range(20):
    bass.extend(riff)

horns = song.add_track(Track(name="horns", instrument="sawtooth", volume=0.4, pan=0.15))
for _ in range(10):
    horns.extend(
        [
            r(4.0),
            Note("Bb", 4, 0.5),
            Note("D", 5, 0.5),
            Note("G", 5, 1.0),
            Note("F", 5, 0.5),
            Note("D", 5, 0.5),
            r(1.0),
        ]
    )

keys = song.add_track(Track(name="keys", instrument="organ", volume=0.3, pan=-0.2))
for _ in range(10):
    keys.extend([Chord("G", "min7", 3, duration=4.0), Chord("C", "min7", 3, duration=4.0)])

song.effects = {
    "horns": EffectsChain()
    .add(reverb, room_size=0.4, wet=0.15)
    .add(compress, threshold=0.5, ratio=3.0),
    "keys": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
}
