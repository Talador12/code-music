"""industrial_grind.py — Industrial. Cm, 110 BPM. Nine Inch Nails aggression.

Distorted everything: grinding bass, metallic percussion, and a screaming
sawtooth lead buried in distortion + compression.

Style: Industrial, Cm, 110 BPM.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    compress,
    distortion,
    highpass,
    reverb,
)

song = Song(title="Industrial Grind", bpm=110)
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.85))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.6))
for _ in range(16):
    kick.extend([Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("E", 4, 1.0), r(0.5), Note("E", 4, 0.5), Note("E", 4, 1.0)])

bass = song.add_track(Track(name="bass", instrument="sawtooth", volume=0.6))
for _ in range(16):
    bass.extend([Note("C", 2, 0.5), Note("C", 2, 0.5), Note("Eb", 2, 0.5), Note("C", 2, 0.5),
                 Note("F", 2, 0.5), Note("Eb", 2, 0.5), Note("C", 2, 0.5), Note("Bb", 1, 0.5)])

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=0.2))
for _ in range(8):
    lead.extend([r(4.0), Note("Eb", 5, 0.5), Note("C", 5, 0.5), Note("Bb", 4, 0.5), Note("C", 5, 0.5),
                 Note("Eb", 5, 1.0), Note("C", 5, 1.0)])

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.2))
for _ in range(8):
    pad.extend([Chord("C", "min", 3, duration=4.0), Chord("Ab", "maj", 3, duration=4.0)])

song.effects = {
    "bass": EffectsChain().add(distortion, drive=3.0, tone=0.4, wet=0.5).add(compress, threshold=0.3, ratio=6.0),
    "lead": EffectsChain().add(distortion, drive=2.5, tone=0.5, wet=0.4).add(reverb, room_size=0.4, wet=0.15),
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35).add(highpass, cutoff_hz=400),
}
