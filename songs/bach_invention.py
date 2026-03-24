"""bach_invention.py — Baroque. Dm, 108 BPM. Two-part harpsichord invention.

Bach's two-part inventions are the textbook of counterpoint — two
independent voices chasing each other. The right hand states the subject,
the left hand answers a fifth below. PolyphonicTrack makes this possible.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    Note,
    PolyphonicTrack,
    Song,
    reverb,
)

song = Song(title="Bach Invention", bpm=108, key_sig="D", time_sig=(4, 4))

BAR = 4.0
E8 = EIGHTH

piano = song.add_polytrack(
    PolyphonicTrack(name="harpsichord", instrument="harpsichord", volume=0.8, pan=0.0)
)

# ── Right hand: subject in D minor ────────────────────────────────────────
rh = [
    (0.0, "D", 5, E8, 0.75),
    (0.5, "E", 5, E8, 0.72),
    (1.0, "F", 5, E8, 0.75),
    (1.5, "G", 5, E8, 0.72),
    (2.0, "A", 5, QUARTER, 0.78),
    (3.0, "G", 5, E8, 0.72),
    (3.5, "F", 5, E8, 0.70),
    # Bar 2
    (4.0, "E", 5, QUARTER, 0.75),
    (5.0, "D", 5, E8, 0.72),
    (5.5, "C", 5, E8, 0.70),
    (6.0, "D", 5, HALF, 0.75),
    # Bar 3: sequence up
    (8.0, "E", 5, E8, 0.72),
    (8.5, "F", 5, E8, 0.70),
    (9.0, "G", 5, E8, 0.72),
    (9.5, "A", 5, E8, 0.75),
    (10.0, "A#", 5, QUARTER, 0.78),
    (11.0, "A", 5, E8, 0.72),
    (11.5, "G", 5, E8, 0.70),
    # Bar 4: cadence
    (12.0, "F", 5, QUARTER, 0.75),
    (13.0, "E", 5, E8, 0.70),
    (13.5, "D", 5, E8, 0.68),
    (14.0, "D", 5, HALF, 0.72),
]
for at, p, o, dur, vel in rh:
    piano.add(Note(p, o, dur, velocity=vel), at=at)

# ── Left hand: answer a fifth below, offset by 2 bars ──────────────────────
for at, p, o, dur, vel in rh:
    from code_music.engine import NOTE_NAMES, note_name_to_midi

    midi = note_name_to_midi(p, o) - 7  # down a fifth
    new_p = NOTE_NAMES[midi % 12]
    new_o = midi // 12 - 1
    piano.add(Note(new_p, new_o, dur, velocity=vel * 0.9), at=at + BAR * 2)

song._effects = {
    "harpsichord": lambda s, sr: reverb(s, sr, room_size=0.45, wet=0.12),
}
