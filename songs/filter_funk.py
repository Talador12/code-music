"""filter_funk.py — Showcases Track.filter() for creative beat sculpting.

A dense drum pattern is duplicated then filtered: one copy keeps only loud
hits, the other keeps only quiet ghost notes. Layered back together with
different panning, creating a wide stereo funk groove.

Style: Funk, Gm, 104 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, compress, reverb

song = Song(title="Filter Funk", bpm=104)

r = Note.rest

# Dense funk hi-hat pattern with accent variation
hat_full = Track(name="hat", instrument="drums_hat", volume=0.45)
accents = [0.9, 0.3, 0.6, 0.3, 0.9, 0.3, 0.5, 0.3, 0.8, 0.3, 0.6, 0.3, 0.9, 0.4, 0.5, 0.3]
for _ in range(12):
    for v in accents:
        hat_full.add(Note("F#", 6, 0.25, velocity=v))

# Filter into loud accents (pan left) and ghost notes (pan right)
hat_accents = hat_full.filter(lambda e: e.velocity > 0.55)
hat_accents.pan = -0.35
hat_accents.name = "hat_accent"

hat_ghosts = hat_full.filter(lambda e: e.velocity <= 0.55)
hat_ghosts.pan = 0.35
hat_ghosts.volume = 0.3
hat_ghosts.name = "hat_ghost"

song.add_track(hat_accents)
song.add_track(hat_ghosts)

# Kick + snare
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.55))
for _ in range(12):
    kick.extend([Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5), r(1.0), Note("C", 2, 1.0)])
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)])

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
riff = [
    Note("G", 2, 0.5),
    r(0.5),
    Note("G", 2, 0.5),
    Note("Bb", 2, 0.5),
    Note("C", 3, 0.5),
    Note("Bb", 2, 0.5),
    Note("G", 2, 0.5),
    r(0.5),
]
for _ in range(12):
    bass.extend(riff)

# Clav
clav = song.add_track(Track(name="clav", instrument="pluck", volume=0.4, pan=0.15))
for _ in range(12):
    clav.extend(
        [
            r(0.5),
            Chord("G", "min", 3, duration=0.5),
            r(0.5),
            Chord("G", "min", 3, duration=0.5),
            r(0.5),
            Chord("C", "min7", 3, duration=0.5),
            r(1.0),
        ]
    )

song.effects = {
    "clav": EffectsChain().add(compress, threshold=0.4, ratio=4.0),
    "bass": EffectsChain().add(reverb, room_size=0.3, wet=0.1),
}
