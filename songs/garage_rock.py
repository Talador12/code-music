"""garage_rock.py — Garage rock. E major, 165 BPM. The Stooges meet The Strokes.

Raw, loud, fast. Distorted power chords, driving drums, and a screaming
lead. Uses EffectsChain with heavy distortion.

Style: Garage rock, E major, 165 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, compress, distortion, reverb

song = Song(title="Garage Rock", bpm=165)
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.6))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35))
for _ in range(16):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)])
    hat.extend([Note("F#", 6, 0.5)] * 8)

guitar = song.add_track(Track(name="guitar", instrument="sawtooth", volume=0.55))
for _ in range(8):
    guitar.extend([
        Chord("E", "maj", 3, duration=4.0), Chord("A", "maj", 3, duration=4.0),
    ])

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
for _ in range(8):
    bass.extend([Note("E", 2, 2.0), Note("E", 2, 1.0), Note("A", 2, 1.0),
                 Note("A", 2, 2.0), Note("B", 2, 1.0), Note("E", 2, 1.0)])

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=0.2))
for _ in range(4):
    lead.extend([
        r(4.0),
        Note("E", 5, 0.5), Note("G#", 5, 0.5), Note("B", 5, 0.5), Note("E", 6, 0.5),
        Note("B", 5, 1.0), Note("G#", 5, 1.0),
        r(4.0),
        Note("A", 5, 0.5), Note("B", 5, 0.5), Note("E", 6, 1.0), r(1.0),
        Note("B", 5, 0.5), Note("G#", 5, 0.5),
    ])

song.effects = {
    "guitar": EffectsChain().add(distortion, drive=3.0, tone=0.5, wet=0.5).add(reverb, room_size=0.35, wet=0.12),
    "lead": EffectsChain().add(distortion, drive=2.0, tone=0.6, wet=0.4).add(compress, threshold=0.4, ratio=4.0),
}
