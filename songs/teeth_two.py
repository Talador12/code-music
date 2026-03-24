"""teeth_two.py — Prog rock. 118 BPM, Em, 6/8 time. Second Teeth album track.

6/8 gives it a rolling, almost waltz-like feel but with rock energy.
Pink Floyd's Echoes has this — that feeling of waves, of long cycles.
Organ-forward with a winding guitar melody and bass that breathes.
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    arp,
    chorus,
    compress,
    crescendo,
    decrescendo,
    delay,
    distortion,
    humanize,
    reverb,
)
from code_music.engine import EIGHTH, QUARTER

song = Song(title="Teeth II", bpm=118, time_sig=(6, 8))

# 6/8: 6 eighth notes per bar = 3.0 quarter beats
BAR = 3.0
E8 = EIGHTH  # 0.5
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── Guitar — winding Dorian melody ───────────────────────────────────────
gtr = song.add_track(Track(name="guitar", instrument="guitar_electric", volume=0.70, pan=-0.15))

# Em Dorian (raised 6th = C# instead of C)
# Opening: sparse arpeggios
intro = arp(Chord("E", "min7", 3), pattern="up_down", rate=E8)
gtr.extend(humanize(intro * 4, vel_spread=0.07))

# Verse melody
verse = humanize(
    [
        Note("E", 4, E8),
        Note("F#", 4, E8),
        Note("G", 4, QUARTER),
        Note("A", 4, E8),
        Note("B", 4, E8),
        Note("A", 4, QUARTER),
        Note("G", 4, E8),
        Note("F#", 4, E8),
        Note("E", 4, QUARTER),
        Note("B", 3, BAR),
        Note("C#", 4, E8),
        Note("D", 4, E8),
        Note("E", 4, QUARTER),
        Note("G", 4, E8),
        Note("A", 4, E8),
        Note("G", 4, QUARTER),
        Note("F#", 4, E8),
        Note("E", 4, E8),
        Note("D", 4, QUARTER),
        Note("E", 4, BAR),
    ],
    vel_spread=0.06,
    timing_spread=0.02,
)
gtr.extend(verse * 2)

# Chorus: chords, more energy
chorus_gtr = crescendo(
    [
        Chord("E", "min", 3, duration=BAR, velocity=0.72),
        Chord("C", "maj", 3, duration=BAR, velocity=0.70),
        Chord("G", "maj", 3, duration=BAR, velocity=0.72),
        Chord("D", "maj", 3, duration=BAR, velocity=0.75),
        Chord("A", "min", 3, duration=BAR, velocity=0.72),
        Chord("E", "min", 3, duration=BAR, velocity=0.73),
        Chord("B", "dom7", 3, duration=BAR, velocity=0.75),
        Chord("E", "min", 3, duration=BAR, velocity=0.70),
    ],
    0.6,
    0.92,
)
gtr.extend(chorus_gtr)

# Bridge: quiet, single notes
gtr.extend(bars(4))
gtr.extend(
    humanize(
        [
            Note("B", 3, BAR),
            Note("A", 3, BAR),
            Note("G", 3, BAR),
            Note("F#", 3, BAR),
        ],
        vel_spread=0.04,
    )
)

# Final chorus: bigger
gtr.extend(crescendo(chorus_gtr, 0.75, 1.0))

# Outro: back to arp
gtr.extend(
    decrescendo(
        humanize(intro * 4, vel_spread=0.07),
        start_vel=0.6,
        end_vel=0.15,
    )
)

# ── Organ — sustained chords ──────────────────────────────────────────────
org = song.add_track(Track(name="organ", instrument="organ", volume=0.45, pan=0.2))
org.extend(bars(4))
org_prog = [
    Chord("E", "min7", 3, duration=BAR * 2),
    Chord("C", "maj7", 3, duration=BAR * 2),
    Chord("G", "maj", 3, duration=BAR * 2),
    Chord("D", "dom7", 3, duration=BAR * 2),
]
org.extend(org_prog * 6)
org.extend(bars(4))

# ── Bass — breathes with the 6/8 wave ────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.72, pan=0.05))
bass.extend(bars(4))
bass_line = [
    Note("E", 2, E8 * 3),
    Note("E", 2, E8),
    Note("F#", 2, E8),
    Note("G", 2, E8),
    Note("C", 3, E8 * 3),
    Note("B", 2, E8),
    Note("A", 2, E8),
    Note("G", 2, E8),
    Note("G", 2, E8 * 3),
    Note("G", 2, E8),
    Note("A", 2, E8),
    Note("B", 2, E8),
    Note("D", 3, E8 * 3),
    Note("C#", 2, E8),
    Note("B", 2, E8),
    Note("A", 2, E8),
] * 4
bass.extend(bass_line)
bass.extend(bars(4))
bass.extend([Note("E", 2, BAR)] * 8)
bass.extend(
    decrescendo(
        [Note("E", 2, BAR)] * 4,
        start_vel=0.7,
        end_vel=0.2,
    )
)

# ── Drums — 6/8 rock feel ─────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.9))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.72))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.38))

kick.extend(bars(4))
# 6/8 kick: beat 1 and beat 4 (E8*0 and E8*3)
kick_6 = [Note("C", 2, E8), r(E8 * 2), Note("C", 2, E8), r(E8 * 2)]
snare_6 = [r(E8 * 2), Note("D", 3, E8), r(E8 * 2), Note("D", 3, E8)]  # off the kick
hat_6 = [Note("F", 5, E8)] * 6

for _ in range(40):
    kick.extend(kick_6)
    snare.extend(snare_6)
    hat.extend(hat_6)
kick.extend(bars(4))
snare.extend(bars(4))
hat.extend(bars(4))

song._effects = {
    "guitar": lambda s, sr: distortion(
        delay(s, sr, delay_ms=152.5, feedback=0.25, wet=0.15),
        drive=1.5,
        tone=0.5,
        wet=0.28,
    ),
    "organ": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.55, wet=0.2), sr, rate_hz=0.4, wet=0.15
    ),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
}
