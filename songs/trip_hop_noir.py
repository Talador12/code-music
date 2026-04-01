"""trip_hop_noir.py — Trip-hop. Dm, 85 BPM. Massive Attack meets Portishead.

Slow, brooding beat with a scratchy vinyl-style pad, deep bass,
and a melancholic Rhodes-like melody. Uses bpm_map for a subtle
accelerando in the last 4 bars.

Style: Trip-hop, Dm, 85 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, bpm_ramp, delay, lowpass, reverb

song = Song(title="Trip Hop Noir", bpm=85)

r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.75))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.5))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.25))
for _ in range(16):
    kick.extend([Note("C", 2, 1.5), r(0.5), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 0.5), r(0.5)])
    hat.extend([Note("F#", 6, 0.5), r(0.5)] * 4)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
for _ in range(16):
    bass.extend([Note("D", 2, 2.0), Note("A", 2, 1.0), Note("Bb", 2, 1.0)])

rhodes = song.add_track(Track(name="rhodes", instrument="piano", volume=0.45, pan=0.15))
for _ in range(8):
    rhodes.extend(
        [
            Note("F", 5, 0.5),
            Note("D", 5, 0.5),
            Note("A", 4, 1.0),
            Note("Bb", 4, 0.5),
            Note("A", 4, 0.5),
            Note("G", 4, 1.0),
            r(4.0),
        ]
    )

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.25))
for _ in range(8):
    pad.extend([Chord("D", "min7", 3, duration=4.0), Chord("Bb", "maj7", 3, duration=4.0)])

# Subtle accelerando in the last 4 bars (beats 49-64)
flat_portion = [85.0] * 48
accel = bpm_ramp(85, 100, bars=4)
song.bpm_map = flat_portion + accel

song.effects = {
    "bass": EffectsChain().add(lowpass, cutoff_hz=180),
    "rhodes": EffectsChain()
    .add(delay, delay_ms=353, feedback=0.2, wet=0.15)
    .add(reverb, room_size=0.55, wet=0.25),
    "pad": EffectsChain().add(reverb, room_size=0.75, wet=0.4),
}
