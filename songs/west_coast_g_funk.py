"""west_coast_g_funk.py — G-funk. Cm, 92 BPM. Dr. Dre meets Warren G.

Classic West Coast hip-hop with a pitched-up sine lead, slow funk drums,
and a deep sub bass. The Chronic meets Regulate.

Style: G-funk, Cm, 92 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, lowpass, reverb

song = Song(title="West Coast G-Funk", bpm=92)

r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.55))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3))
for _ in range(16):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 0.5), r(0.5), Note("C", 2, 1.0)])
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)])
    hat.extend([Note("F#", 6, 0.5)] * 8)

bass = song.add_track(Track(name="bass", instrument="sine", volume=0.65))
for _ in range(16):
    bass.extend([Note("C", 2, 1.5), Note("C", 2, 0.5), r(1.0), Note("Eb", 2, 1.0)])

# G-funk whine lead (sine, high octave)
lead = song.add_track(Track(name="whine", instrument="sine", volume=0.4, pan=0.2))
whine = [
    Note("Eb", 6, 0.5),
    Note("C", 6, 0.5),
    Note("Bb", 5, 0.5),
    r(0.5),
    Note("Ab", 5, 0.5),
    Note("Bb", 5, 0.5),
    Note("C", 6, 1.0),
]
for _ in range(8):
    lead.extend(whine + [r(4.0)])

keys = song.add_track(Track(name="keys", instrument="organ", volume=0.3, pan=-0.15))
for _ in range(8):
    keys.extend(
        [
            Chord("C", "min7", 4, duration=4.0),
            Chord("Ab", "maj7", 3, duration=4.0),
        ]
    )

song.effects = {
    "bass": EffectsChain().add(lowpass, cutoff_hz=150),
    "whine": EffectsChain().add(delay, delay_ms=240, feedback=0.2, wet=0.15),
    "keys": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
}
