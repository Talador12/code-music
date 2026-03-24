"""nocturne_op2.py — Classical piano via PolyphonicTrack. F minor, 56 BPM.

A proper piano nocturne where the left hand plays sustained arpeggiated
chords while the right hand sings a melody above — both hands independent,
notes overlapping. This is what PolyphonicTrack was built for.

Chopin's nocturnes work because the left hand creates a harmonic bed
that the right hand floats over. The sustain pedal (implied here by
long note durations) lets everything ring together.
"""

from code_music import (
    DOTTED_HALF,
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    WHOLE,
    Note,
    PolyphonicTrack,
    Song,
    conv_reverb,
)

song = Song(title="Nocturne Op. 2", bpm=56, key_sig="F", time_sig=(4, 4))

BAR = 4.0

# ── PolyphonicTrack piano — left + right hand simultaneously ──────────────
piano = song.add_polytrack(PolyphonicTrack(name="piano", instrument="piano", volume=0.85, pan=0.0))

# ── Left hand: arpeggiated chords, sustained ──────────────────────────────
# Each chord tone placed at a slight offset to create the rolling arpeggio feel
lh_chords = [
    # Bar 1: Fm  (F Ab C)
    ("F", 2, WHOLE, 0.0, 0.45),
    ("C", 3, WHOLE, 0.25, 0.40),
    ("F", 3, DOTTED_HALF, 0.5, 0.38),
    ("G#", 3, HALF, 0.75, 0.35),
    # Bar 2: Db maj7  (Db F Ab C)
    ("C#", 2, WHOLE, BAR, 0.45),
    ("F", 3, WHOLE, BAR + 0.25, 0.40),
    ("G#", 3, DOTTED_HALF, BAR + 0.5, 0.38),
    ("C", 4, HALF, BAR + 0.75, 0.35),
    # Bar 3: Bbm7  (Bb Db F Ab)
    ("A#", 1, WHOLE, BAR * 2, 0.45),
    ("C#", 3, WHOLE, BAR * 2 + 0.25, 0.40),
    ("F", 3, DOTTED_HALF, BAR * 2 + 0.5, 0.38),
    ("G#", 3, HALF, BAR * 2 + 0.75, 0.35),
    # Bar 4: C7  (C E G Bb)
    ("C", 2, WHOLE, BAR * 3, 0.48),
    ("E", 3, WHOLE, BAR * 3 + 0.25, 0.42),
    ("G", 3, DOTTED_HALF, BAR * 3 + 0.5, 0.40),
    ("A#", 3, HALF, BAR * 3 + 0.75, 0.38),
    # Bar 5-8: repeat with slight dynamic variation
    ("F", 2, WHOLE, BAR * 4, 0.50),
    ("C", 3, WHOLE, BAR * 4 + 0.25, 0.45),
    ("F", 3, DOTTED_HALF, BAR * 4 + 0.5, 0.42),
    ("G#", 3, HALF, BAR * 4 + 0.75, 0.40),
    ("C#", 2, WHOLE, BAR * 5, 0.50),
    ("F", 3, WHOLE, BAR * 5 + 0.25, 0.45),
    ("G#", 3, DOTTED_HALF, BAR * 5 + 0.5, 0.42),
    ("C", 4, HALF, BAR * 5 + 0.75, 0.40),
    ("A#", 1, WHOLE, BAR * 6, 0.52),
    ("C#", 3, WHOLE, BAR * 6 + 0.25, 0.47),
    ("F", 3, DOTTED_HALF, BAR * 6 + 0.5, 0.44),
    ("G#", 3, HALF, BAR * 6 + 0.75, 0.42),
    ("C", 2, WHOLE, BAR * 7, 0.55),
    ("E", 3, WHOLE, BAR * 7 + 0.25, 0.48),
    ("G", 3, DOTTED_HALF, BAR * 7 + 0.5, 0.45),
    ("A#", 3, HALF, BAR * 7 + 0.75, 0.42),
]
for pitch, oct, dur, at, vel in lh_chords:
    piano.add(Note(pitch, oct, dur, velocity=vel), at=at)

# ── Right hand: singing melody above the chords ──────────────────────────
rh_melody = [
    # Bar 1-2: opening phrase
    (1.0, "F", 5, DOTTED_QUARTER, 0.68),
    (2.5, "G#", 5, EIGHTH, 0.62),
    (3.0, "G", 5, HALF, 0.70),
    (BAR + 0.0, "G#", 5, QUARTER, 0.65),
    (BAR + 1.0, "A#", 5, HALF, 0.72),
    (BAR + 3.0, "G#", 5, QUARTER, 0.65),
    # Bar 3-4: answer phrase
    (BAR * 2 + 0.0, "F", 5, DOTTED_QUARTER, 0.68),
    (BAR * 2 + 1.5, "G", 5, EIGHTH, 0.62),
    (BAR * 2 + 2.0, "G#", 5, HALF, 0.72),
    (BAR * 3 + 0.0, "G", 5, QUARTER, 0.65),
    (BAR * 3 + 1.0, "F", 5, HALF, 0.70),
    (BAR * 3 + 3.0, "E", 5, QUARTER, 0.60),
    # Bar 5-6: more expressive — higher peak
    (BAR * 4 + 0.0, "F", 5, QUARTER, 0.72),
    (BAR * 4 + 1.0, "G#", 5, QUARTER, 0.75),
    (BAR * 4 + 2.0, "C", 6, DOTTED_HALF, 0.82),
    (BAR * 5 + 1.5, "A#", 5, EIGHTH, 0.70),
    (BAR * 5 + 2.0, "G#", 5, HALF, 0.75),
    # Bar 7-8: descent, closing
    (BAR * 6 + 0.0, "G", 5, QUARTER, 0.68),
    (BAR * 6 + 1.0, "F", 5, QUARTER, 0.65),
    (BAR * 6 + 2.0, "C#", 5, HALF, 0.62),
    (BAR * 7 + 0.0, "C", 5, DOTTED_QUARTER, 0.60),
    (BAR * 7 + 1.5, "A#", 4, EIGHTH, 0.55),
    (BAR * 7 + 2.0, "F", 4, WHOLE, 0.50),
]
for at, pitch, oct, dur, vel in rh_melody:
    piano.add(Note(pitch, oct, dur, velocity=vel), at=at)

song._effects = {
    "piano": lambda s, sr: conv_reverb(s, sr, room="chamber", wet=0.32),
}
