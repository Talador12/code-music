"""Dark arp: Phrygian mode, hoover synth, minor arpeggios, 120 BPM.

Alluring. Pulls you in like a current. Phrygian gives it that
flamenco-meets-techno dark flavor. You don't walk away from this.
"""

from code_music import Chord, Note, Song, Track, arp, delay, lfo_filter, phaser, reverb

song = Song(title="dark_arp", bpm=120)

# Phrygian: E - F - G - Am - Bdim - C - D
pad = song.add_track(Track(name="pad", instrument="supersaw", volume=0.4, pan=0.0))
for ch, sh in [("E", "min"), ("F", "maj"), ("G", "maj"), ("A", "min")] * 2:
    pad.add(Chord(ch, sh, 3, duration=4.0, velocity=0.5))

# Hoover arp — the alluring hook
arp_tr = song.add_track(Track(name="arp", instrument="hoover", volume=0.6, pan=0.15))
for ch, sh in [("E", "min7"), ("F", "maj7"), ("G", "maj"), ("A", "min7")] * 2:
    arp_tr.extend(arp(Chord(ch, sh, 4), pattern="up", rate=0.25, octaves=2))

# Kick + hat for structure
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.9))
kick.extend([Note("C", 2, 1.0)] * 32)
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35))
hat.extend([Note.rest(0.5), Note("F", 5, 0.5)] * 32)

song.effects = {
    "pad": lambda s, sr: lfo_filter(
        reverb(s, sr, room_size=0.5, wet=0.2), sr, rate_hz=0.12, min_cutoff=200.0, max_cutoff=4500.0
    ),
    "arp": lambda s, sr: phaser(
        delay(s, sr, delay_ms=187.5, feedback=0.3, wet=0.2), sr, rate_hz=0.25, wet=0.35
    ),
}
