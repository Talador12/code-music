"""duende.py — Flamenco. Phrygian dominant, E, 140 BPM. Cajon + acoustic guitar.

'Duende' is the Spanish term for the dark, inexplicable power some music has —
the quality that gives you chills not from prettiness but from something
ancient and true. Phrygian dominant (1 b2 3 4 5 b6 b7) is the flamenco scale:
that raised 3rd against the flat 2nd is the whole sound.
Cajon percussion, acoustic guitar, and nothing else.
"""

from code_music import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    Note,
    Song,
    Track,
    crescendo,
    humanize,
    reverb,
)

song = Song(title="Duende", bpm=140)

BAR = 4.0
r = Note.rest

# ── Cajon — flamenco rhythm (12-beat cycle: 1.2.3.4.5.6.7.8.9.10.11.12)
# Simplified to 4/4 with accents on 1, 3, 5, 8, 10
caj_kick = song.add_track(Track(name="cajon_low", instrument="drums_kick", volume=0.88))
caj_snap = song.add_track(Track(name="cajon_snap", instrument="drums_snare", volume=0.72))
caj_slap = song.add_track(Track(name="cajon_slap", instrument="drums_clap", volume=0.65))

# Bulería-inspired pattern
buleria_kick = [
    Note("C", 2, EIGHTH),
    r(EIGHTH),
    Note("C", 2, EIGHTH),
    r(EIGHTH),
    r(EIGHTH),
    Note("C", 2, EIGHTH),
    r(EIGHTH),
    Note("C", 2, EIGHTH),
]
buleria_snap = [
    r(EIGHTH),
    Note("D", 3, EIGHTH),
    r(QUARTER),
    r(EIGHTH),
    Note("D", 3, EIGHTH),
    r(QUARTER),
]
buleria_slap = [
    r(QUARTER),
    r(EIGHTH),
    Note("D", 3, EIGHTH),
    Note("D", 3, EIGHTH),
    r(EIGHTH),
    Note("D", 3, QUARTER),
]
for _ in range(16):
    caj_kick.extend(buleria_kick)
    caj_snap.extend(buleria_snap)
    caj_slap.extend(buleria_slap)

# ── Acoustic guitar — Phrygian dominant in E ─────────────────────────────
# E Phrygian dominant: E F G# A B C D
gtr = song.add_track(Track(name="guitar", instrument="guitar_acoustic", volume=0.82, pan=-0.1))

# Opening: dramatic E chord strums then a fast scale run
strum_open = humanize(
    [
        Note("E", 3, QUARTER, velocity=0.9),
        Note("E", 3, EIGHTH, velocity=0.75),
        r(EIGHTH),
        Note("F", 3, QUARTER, velocity=0.85),
        Note("E", 3, HALF, velocity=0.88),
    ]
    * 4,
    vel_spread=0.08,
)
gtr.extend(strum_open)

# Falseta (melodic phrase) — the characteristic phrygian dominant run
phrygian_dom_notes = [
    Note("E", 5, EIGHTH),
    Note("D", 5, EIGHTH),
    Note("C", 5, EIGHTH),
    Note("B", 4, EIGHTH),
    Note("A", 4, EIGHTH),
    Note("G#", 4, EIGHTH),
    Note("F", 4, EIGHTH),
    Note("E", 4, EIGHTH),
]
reverse_run = list(reversed(phrygian_dom_notes))

falseta = humanize(
    crescendo(
        phrygian_dom_notes
        + reverse_run
        + [
            Note("E", 4, QUARTER),
            Note("F", 4, EIGHTH),
            Note("E", 4, EIGHTH),
            Note("G#", 4, QUARTER),
            Note("A", 4, QUARTER),
            Note("E", 4, HALF),
            r(HALF),
        ],
        start_vel=0.6,
        end_vel=0.95,
    ),
    vel_spread=0.06,
    timing_spread=0.02,
)
gtr.extend(falseta)

# Main section: chord vamp with melodic interjections
chord_vamp = humanize(
    [
        Note("E", 3, DOTTED_QUARTER, velocity=0.88),
        Note("E", 3, EIGHTH, velocity=0.72),
        Note("F", 3, QUARTER, velocity=0.82),
        Note("E", 3, HALF, velocity=0.85),
    ]
    * 8,
    vel_spread=0.09,
)
gtr.extend(chord_vamp)

# Return falseta, faster
fast_run = humanize(
    [
        Note("E", 5, EIGHTH / 2),
        Note("D", 5, EIGHTH / 2),
        Note("C", 5, EIGHTH / 2),
        Note("B", 4, EIGHTH / 2),
        Note("A", 4, EIGHTH / 2),
        Note("G#", 4, EIGHTH / 2),
        Note("F", 4, EIGHTH / 2),
        Note("E", 4, EIGHTH / 2),
        Note("E", 4, HALF),
        r(HALF),
        Note("E", 5, HALF, velocity=1.0),
        r(HALF),
    ],
    vel_spread=0.05,
    timing_spread=0.015,
)
gtr.extend(fast_run)

song._effects = {
    "guitar": lambda s, sr: reverb(s, sr, room_size=0.45, damping=0.5, wet=0.12),
}
