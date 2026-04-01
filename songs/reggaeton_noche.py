"""reggaeton_noche.py — Reggaeton. Gm, 95 BPM. Dembow riddim.

The classic dembow pattern with booming 808, sparse piano chords,
and a dark melodic lead. Uses Track.loop for the hypnotic bass pattern.

Style: Reggaeton, Gm, 95 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, compress, delay, lowpass, reverb

song = Song(title="Reggaeton Noche", bpm=95)

r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.85))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.55))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35))
for _ in range(16):
    # Dembow pattern
    kick.extend(
        [
            Note("C", 2, 0.75),
            r(0.25),
            Note("C", 2, 0.5),
            r(0.5),
            Note("C", 2, 0.5),
            r(0.5),
            Note("C", 2, 0.75),
            r(0.25),
        ]
    )
    snare.extend(
        [
            r(0.75),
            Note("E", 4, 0.25),
            r(0.5),
            Note("E", 4, 0.5),
            r(0.5),
            Note("E", 4, 0.5),
            r(0.5),
            Note("E", 4, 0.5),
        ]
    )
    hat.extend([Note("F#", 6, 0.25)] * 16)

bass_bar = Track(name="808", instrument="sine", volume=0.7)
bass_bar.extend(
    [
        Note("G", 2, 1.5),
        Note("G", 2, 0.5),
        r(1.0),
        Note("Bb", 2, 1.0),
    ]
)
song.add_track(bass_bar.loop(16))

piano = song.add_track(Track(name="piano", instrument="piano", volume=0.35, pan=0.1))
for _ in range(8):
    piano.extend(
        [
            r(2.0),
            Chord("G", "min", 4, duration=0.5),
            r(0.5),
            Chord("G", "min", 4, duration=0.5),
            r(0.5),
            r(2.0),
            Chord("Eb", "maj", 4, duration=0.5),
            r(0.5),
            Chord("D", "min", 4, duration=0.5),
            r(0.5),
        ]
    )

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.4, pan=-0.15))
for _ in range(8):
    lead.extend(
        [
            Note("D", 5, 0.5),
            Note("Eb", 5, 0.5),
            Note("G", 5, 0.5),
            r(0.5),
            Note("F", 5, 0.5),
            Note("Eb", 5, 0.5),
            Note("D", 5, 1.0),
            r(4.0),
        ]
    )

song.effects = {
    "808": EffectsChain().add(lowpass, cutoff_hz=150).add(compress, threshold=0.4, ratio=5.0),
    "lead": EffectsChain()
    .add(delay, delay_ms=315, feedback=0.2, wet=0.15)
    .add(reverb, room_size=0.4, wet=0.15),
}
