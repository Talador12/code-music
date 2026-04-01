"""dnb_neurofunk.py — Neurofunk DnB. Fm, 174 BPM. Dark rolling basslines.

Heavy reese bass with Track.loop, chopped breakbeat, and a filtered pad.
Uses Track.stretch on the bass for the half-time breakdown.

Style: Neurofunk drum and bass, Fm, 174 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, distortion, highpass, lowpass, reverb

song = Song(title="DnB Neurofunk", bpm=174)

r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.85))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.6))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35))
for _ in range(24):
    kick.extend(
        [
            Note("C", 2, 0.5),
            r(0.25),
            Note("C", 2, 0.25),
            r(0.5),
            Note("C", 2, 0.5),
            r(0.5),
            Note("C", 2, 0.25),
            r(0.25),
            Note("C", 2, 0.5),
            r(0.5),
        ]
    )
    snare.extend(
        [
            r(1.0),
            Note("E", 4, 0.5),
            r(0.5),
            Note("E", 4, 0.25),
            r(0.25),
            Note("E", 4, 0.5),
            r(0.5),
            Note("E", 4, 0.5),
            r(0.5),
        ]
    )
    hat.extend([Note("F#", 6, 0.25)] * 16)

bass_bar = Track(name="bass", instrument="bass", volume=0.7)
bass_bar.extend(
    [
        Note("F", 2, 0.25),
        Note("F", 2, 0.25),
        Note("Ab", 2, 0.25),
        Note("F", 2, 0.25),
        Note("F", 2, 0.25),
        Note("C", 3, 0.25),
        Note("F", 2, 0.25),
        Note("Eb", 2, 0.25),
        Note("Db", 2, 0.25),
        Note("F", 2, 0.25),
        Note("F", 2, 0.25),
        Note("Ab", 2, 0.25),
        Note("F", 2, 0.25),
        Note("Eb", 2, 0.25),
        Note("F", 2, 0.25),
        Note("C", 2, 0.25),
    ]
)
main_bass = bass_bar.loop(16)
slow_bass = bass_bar.stretch(2.0).loop(4)
song.add_track(main_bass.concat(slow_bass).concat(main_bass))

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.2))
for _ in range(12):
    pad.extend([Chord("F", "min", 3, duration=4.0), Chord("Db", "maj", 3, duration=4.0)])

song.effects = {
    "bass": EffectsChain()
    .add(distortion, drive=2.0, tone=0.4, wet=0.3)
    .add(lowpass, cutoff_hz=250),
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35).add(highpass, cutoff_hz=400),
}
