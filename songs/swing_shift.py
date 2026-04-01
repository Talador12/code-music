"""swing_shift.py — Big band swing. Bb major, 160 BPM. Count Basie energy.

A swinging big band number with walking bass, brass stabs, and a
saxophone-style lead. Classic 12-bar blues structure over 4 choruses.

Style: Big band swing, Bb major, 160 BPM.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    compress,
    reverb,
)

song = Song(title="Swing Shift", bpm=160)

r = Note.rest

# ── Walking bass ──────────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6, pan=-0.1))
walk_I = [Note("Bb", 2, 1.0), Note("D", 3, 1.0), Note("F", 3, 1.0), Note("D", 3, 1.0)]
walk_IV = [Note("Eb", 2, 1.0), Note("G", 2, 1.0), Note("Bb", 2, 1.0), Note("G", 2, 1.0)]
walk_V = [Note("F", 2, 1.0), Note("A", 2, 1.0), Note("C", 3, 1.0), Note("A", 2, 1.0)]

blues_12 = walk_I * 4 + walk_IV * 2 + walk_I * 2 + walk_V + walk_IV + walk_I * 2
for _ in range(4):
    bass.extend(blues_12)

# ── Piano comping — 2-and-4 stabs ────────────────────────────────────────
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.4, pan=0.15))
stab_I = [
    r(1.0),
    Chord("Bb", "dom7", 3, duration=1.0),
    r(1.0),
    Chord("Bb", "dom7", 3, duration=1.0),
]
stab_IV = [
    r(1.0),
    Chord("Eb", "dom7", 3, duration=1.0),
    r(1.0),
    Chord("Eb", "dom7", 3, duration=1.0),
]
stab_V = [r(1.0), Chord("F", "dom7", 3, duration=1.0), r(1.0), Chord("F", "dom7", 3, duration=1.0)]

piano_12 = stab_I * 4 + stab_IV * 2 + stab_I * 2 + stab_V + stab_IV + stab_I * 2
for _ in range(4):
    piano.extend(piano_12)

# ── Drums — swing pattern ────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35))
for _ in range(48):
    kick.extend([Note("C", 2, 2.0), Note("C", 2, 2.0)])
    hat.extend(
        [
            Note("F#", 6, 0.67),
            Note("F#", 6, 0.33),
            Note("F#", 6, 0.67),
            Note("F#", 6, 0.33),
            Note("F#", 6, 0.67),
            Note("F#", 6, 0.33),
            Note("F#", 6, 0.67),
            Note("F#", 6, 0.33),
        ]
    )

# ── Sax lead — pentatonic licks ──────────────────────────────────────────
sax = song.add_track(Track(name="sax", instrument="sawtooth", volume=0.5, pan=0.2))
lick_a = [
    Note("Bb", 4, 0.5),
    Note("D", 5, 0.5),
    Note("F", 5, 0.5),
    Note("Eb", 5, 0.5),
    Note("D", 5, 1.0),
    Note("Bb", 4, 1.0),
]
lick_b = [
    Note("F", 5, 0.5),
    Note("Eb", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("Bb", 4, 1.0),
    r(1.0),
]
lick_rest = [r(4.0)]
sax_12 = lick_a + lick_b + lick_a + lick_rest + lick_b + lick_rest + lick_a + lick_b + lick_rest * 4
for _ in range(4):
    sax.extend(sax_12)

song.effects = {
    "sax": EffectsChain()
    .add(reverb, room_size=0.45, wet=0.18)
    .add(compress, threshold=0.5, ratio=3.0),
    "piano": EffectsChain().add(reverb, room_size=0.4, wet=0.15),
}
