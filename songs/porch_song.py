"""porch_song.py — Folk / Acoustic. Karplus-Strong guitar, G major, 84 BPM.

That Nick Drake / Iron & Wine intimacy. A single Karplus-Strong guitar
doing the fingerpicking work, a second voice harmonizing a third above,
and just barely a bass underneath. Nothing processed. Just wood and air.

The Karplus-Strong synthesis models an actual plucked string — noise seed
into a feedback delay loop with a lowpass filter. Sounds fundamentally
different from additive synthesis. More real.
"""

from code_music import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    Note,
    Song,
    Track,
    decrescendo,
    humanize,
    reverb,
)

song = Song(title="Porch Song", bpm=84, key_sig="G")

r = Note.rest


def bars(n):
    return [r(4.0)] * n


# ── Primary guitar — Karplus-Strong ──────────────────────────────────────
gtr = song.add_track(Track(name="guitar", instrument="guitar_ks", volume=0.82, pan=-0.1))

# G major fingerpicking pattern — thumb on bass, fingers on melody
intro = humanize(
    [
        Note("G", 3, EIGHTH),
        Note("B", 4, EIGHTH),
        Note("D", 5, EIGHTH),
        Note("B", 4, EIGHTH),
        Note("G", 3, EIGHTH),
        Note("D", 5, EIGHTH),
        Note("B", 4, EIGHTH),
        Note("D", 5, EIGHTH),
        Note("C", 3, EIGHTH),
        Note("G", 4, EIGHTH),
        Note("E", 5, EIGHTH),
        Note("G", 4, EIGHTH),
        Note("C", 3, EIGHTH),
        Note("E", 5, EIGHTH),
        Note("G", 4, EIGHTH),
        Note("E", 5, EIGHTH),
        Note("E", 3, EIGHTH),
        Note("G", 4, EIGHTH),
        Note("B", 4, EIGHTH),
        Note("G", 4, EIGHTH),
        Note("E", 3, EIGHTH),
        Note("B", 4, EIGHTH),
        Note("G", 4, EIGHTH),
        Note("B", 4, EIGHTH),
        Note("D", 3, EIGHTH),
        Note("A", 4, EIGHTH),
        Note("F#", 5, EIGHTH),
        Note("A", 4, EIGHTH),
        Note("D", 3, EIGHTH),
        Note("F#", 5, EIGHTH),
        Note("A", 4, EIGHTH),
        Note("F#", 5, EIGHTH),
    ],
    vel_spread=0.1,
    timing_spread=0.04,
)
gtr.extend(intro)

# Verse: melody emerges from the arpeggio texture
verse_mel = humanize(
    [
        Note("G", 4, DOTTED_QUARTER),
        Note("A", 4, EIGHTH),
        Note("B", 4, HALF),
        Note("C", 5, DOTTED_QUARTER),
        Note("B", 4, EIGHTH),
        Note("A", 4, HALF),
        Note("G", 4, DOTTED_QUARTER),
        Note("F#", 4, EIGHTH),
        Note("E", 4, HALF),
        Note("D", 4, HALF),
        r(HALF),
        Note("D", 5, DOTTED_QUARTER),
        Note("C", 5, EIGHTH),
        Note("B", 4, HALF),
        Note("A", 4, DOTTED_QUARTER),
        Note("G", 4, EIGHTH),
        Note("F#", 4, HALF),
        Note("G", 4, DOTTED_QUARTER),
        Note("A", 4, EIGHTH),
        Note("B", 4, QUARTER),
        Note("C", 5, QUARTER),
        Note("G", 4, HALF * 2),
    ],
    vel_spread=0.08,
    timing_spread=0.04,
)
gtr.extend(verse_mel)

# Outro: back to arpeggio, decrescendo
outro = decrescendo(humanize(intro[:16], vel_spread=0.1), start_vel=0.75, end_vel=0.2)
gtr.extend(outro)

# ── Harmony guitar — higher, KS too ──────────────────────────────────────
harm = song.add_track(Track(name="harm", instrument="guitar_ks", volume=0.45, pan=0.3))
harm.extend(bars(4))  # enters after intro
harm.extend(
    humanize(
        [
            Note("B", 4, DOTTED_QUARTER),
            Note("C", 5, EIGHTH),
            Note("D", 5, HALF),
            Note("E", 5, DOTTED_QUARTER),
            Note("D", 5, EIGHTH),
            Note("C", 5, HALF),
            Note("B", 4, DOTTED_QUARTER),
            Note("A", 4, EIGHTH),
            Note("G", 4, HALF),
            Note("F#", 4, HALF),
            r(HALF),
            Note("F#", 5, DOTTED_QUARTER),
            Note("E", 5, EIGHTH),
            Note("D", 5, HALF),
            Note("C", 5, DOTTED_QUARTER),
            Note("B", 4, EIGHTH),
            Note("A", 4, HALF),
            Note("B", 4, DOTTED_QUARTER),
            Note("C", 5, EIGHTH),
            Note("D", 5, QUARTER),
            Note("E", 5, QUARTER),
            Note("B", 4, HALF * 2),
        ],
        vel_spread=0.07,
    )
)

# ── Bass — very sparse, just root notes ──────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="guitar_ks", volume=0.55, pan=0.05))
bass_line = humanize(
    [
        Note("G", 2, 4.0),
        Note("C", 2, 4.0),
        Note("E", 2, 4.0),
        Note("D", 2, 4.0),
    ]
    * 3,
    vel_spread=0.06,
)
bass.extend(bass_line)

song._effects = {
    "guitar": lambda s, sr: reverb(s, sr, room_size=0.5, damping=0.5, wet=0.15),
    "harm": lambda s, sr: reverb(s, sr, room_size=0.55, wet=0.18),
    "bass": lambda s, sr: reverb(s, sr, room_size=0.4, wet=0.12),
}
