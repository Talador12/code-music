"""flamenco_fire.py — Flamenco. E Phrygian, 115 BPM. Passionate guitar and palmas.

Rapid flamenco guitar arpeggios, clapping rhythm (palmas), and a cajón groove.
Uses Track.loop for the repeating rasgueado pattern.

Style: Flamenco, E Phrygian, 115 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb

song = Song(title="Flamenco Fire", bpm=115)

r = Note.rest

# Cajón (kick + snare)
cajon_kick = song.add_track(Track(name="cajon_low", instrument="drums_kick", volume=0.7))
cajon_slap = song.add_track(Track(name="cajon_slap", instrument="drums_snare", volume=0.5))
for _ in range(20):
    cajon_kick.extend([Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5), r(1.0), Note("C", 2, 1.0)])
    cajon_slap.extend(
        [
            r(1.0),
            Note("E", 4, 0.5),
            Note("E", 4, 0.5),
            r(0.5),
            Note("E", 4, 0.5),
            r(0.5),
            Note("E", 4, 0.5),
        ]
    )

# Palmas (claps) — syncopated
palmas = song.add_track(Track(name="palmas", instrument="drums_hat", volume=0.35))
for _ in range(20):
    palmas.extend(
        [
            r(0.5),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25),
            r(0.5),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25),
            r(0.25),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25),
            r(0.5),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25),
        ]
    )

# Guitar rasgueado (rapid strumming) — loop a one-bar pattern
guitar_bar = Track(name="guitar", instrument="pluck", volume=0.55, pan=0.15)
guitar_bar.extend(
    [
        Note("E", 4, 0.25),
        Note("G", 4, 0.25),
        Note("B", 4, 0.25),
        Note("E", 5, 0.25),
        Note("F", 4, 0.25),
        Note("A", 4, 0.25),
        Note("C", 5, 0.25),
        Note("F", 5, 0.25),
        Note("E", 4, 0.25),
        Note("G#", 4, 0.25),
        Note("B", 4, 0.25),
        Note("E", 5, 0.25),
        Note("A", 3, 0.5),
        Note("B", 3, 0.5),
    ]
)
song.add_track(guitar_bar.loop(20))

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55))
for _ in range(20):
    bass.extend([Note("E", 2, 2.0), Note("F", 2, 1.0), Note("E", 2, 1.0)])

# Chords
chords = song.add_track(Track(name="chords", instrument="pad", volume=0.2))
for _ in range(10):
    chords.extend(
        [
            Chord("E", "min", 3, duration=4.0),
            Chord("F", "maj", 3, duration=4.0),
        ]
    )

song.effects = {
    "guitar": EffectsChain().add(reverb, room_size=0.4, wet=0.18),
    "chords": EffectsChain().add(reverb, room_size=0.65, wet=0.3),
}
