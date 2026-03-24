"""still_water.py — Neo-classical / minimal piano. C minor, 66 BPM.

Nils Frahm / Ólafur Arnalds territory. A single piano voice, no
ornamentation. Notes played with weight. Long sustains. The silences
matter as much as the notes. No drums. No accompaniment beyond soft strings
entering in the second half. This is music that requires nothing of you
except to be in the room with it.
"""

from code_music import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    WHOLE,
    Note,
    Song,
    Track,
    crescendo,
    decrescendo,
    delay,
    humanize,
    reverb,
)

song = Song(title="Still Water", bpm=66)

BAR = 4.0
r = Note.rest

# ── Piano — the entire song ───────────────────────────────────────────────
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.82, pan=0.0))

# Section A: sparse, finding its way
sect_a = humanize(
    [
        Note("C", 4, HALF),
        r(HALF),
        Note("G", 4, QUARTER),
        Note("F", 4, QUARTER),
        r(HALF),
        Note("D#", 4, HALF),
        r(QUARTER),
        Note("G", 4, QUARTER),
        Note("C", 4, WHOLE),
        r(BAR),
        Note("G", 3, HALF),
        Note("A#", 3, HALF),
        Note("F", 4, QUARTER),
        Note("D#", 4, QUARTER),
        Note("D", 4, HALF),
        Note("C", 4, WHOLE),
        r(BAR),
    ],
    vel_spread=0.09,
    timing_spread=0.06,
)

# Section B: melody emerges, more confident
sect_b = humanize(
    crescendo(
        [
            Note("C", 5, DOTTED_QUARTER),
            Note("D", 5, EIGHTH),
            Note("D#", 5, HALF),
            Note("G", 5, QUARTER),
            Note("F", 5, QUARTER),
            Note("D#", 5, HALF),
            Note("D", 5, HALF),
            Note("C", 5, WHOLE),
            r(HALF),
            Note("G", 4, DOTTED_QUARTER),
            Note("A#", 4, EIGHTH),
            Note("C", 5, HALF),
            Note("D", 5, QUARTER),
            Note("C", 5, QUARTER),
            Note("A#", 4, HALF),
            Note("G", 4, WHOLE),
        ],
        start_vel=0.38,
        end_vel=0.82,
    ),
    vel_spread=0.07,
    timing_spread=0.05,
)

# Section C: decrescendo back to stillness
sect_c = humanize(
    decrescendo(
        [
            Note("C", 5, HALF),
            Note("G", 4, HALF),
            Note("D#", 4, HALF),
            Note("C", 4, HALF),
            Note("G", 3, WHOLE),
            r(HALF),
            Note("C", 4, HALF),
            Note("G", 3, WHOLE),
            r(BAR),
            Note("C", 3, WHOLE * 2),
        ],
        start_vel=0.75,
        end_vel=0.12,
    ),
    vel_spread=0.06,
    timing_spread=0.07,
)

piano.extend(sect_a)
piano.extend(sect_b)
piano.extend(sect_a)  # return
piano.extend(sect_c)

# ── Strings — enter only in section B, very quiet ────────────────────────
n_a = len(sect_a)
n_b = len(sect_b)
rest_beats = sum(n.duration for n in sect_a)

strings = song.add_track(Track(name="strings", instrument="strings", volume=0.28, pan=-0.2))
# Silence during A
strings.add(r(rest_beats))
# Breathe in during B
strings.extend(
    crescendo(
        [
            Note("C", 4, HALF * 4),
            Note("G", 3, HALF * 4),
            Note("D#", 3, HALF * 4),
            Note("C", 3, HALF * 4),
        ],
        start_vel=0.05,
        end_vel=0.35,
    )
)
# Back to silence
strings.add(r(rest_beats))
# Fade out with sect_c
strings.extend(
    decrescendo(
        [
            Note("C", 3, HALF * 4),
        ],
        start_vel=0.3,
        end_vel=0.0,
    )
)

song._effects = {
    "piano": lambda s, sr: delay(
        reverb(s, sr, room_size=0.72, damping=0.35, wet=0.28),
        sr,
        delay_ms=909.0,
        feedback=0.3,
        wet=0.15,
    ),
    "strings": lambda s, sr: reverb(s, sr, room_size=0.88, wet=0.4),
}
