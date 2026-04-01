"""conversations.py — Jazz / neo-classical. Dm, 80 BPM.

Showcases PolyphonicTrack: a piano where the left hand (bass + chords)
and right hand (melody) are written as simultaneous notes that sustain
independently, just like a real pianist would play.

Regular Track forces notes to be sequential. PolyphonicTrack lets any
note start and sustain at any beat offset — the left hand chord on beat 0
keeps ringing while the right hand melody enters at beat 0.5.
"""

from code_music import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    WHOLE,
    Note,
    PolyphonicTrack,
    Song,
    Track,
    conv_reverb,
    delay,
    humanize,
    reverb,
)

song = Song(title="Conversations", bpm=80)

BAR = 4.0
r = Note.rest

# ── PolyphonicTrack piano — left + right hand simultaneously ──────────────
piano = song.add_polytrack(PolyphonicTrack(name="piano", instrument="piano", volume=0.82, pan=0.0))

# Left hand: bass notes + sustained chords (they ring while melody plays)
lh_chords = [
    # Bar 1: Dm7 chord sustained, bass note walks
    ("D", 3, WHOLE, 0.0),
    ("F", 3, WHOLE, 0.0),
    ("A", 3, HALF, 0.0),
    ("D", 2, QUARTER, 0.0),
    # Bar 2
    ("G", 3, WHOLE, BAR),
    ("B", 3, WHOLE, BAR),
    ("D", 4, HALF, BAR),
    ("G", 2, QUARTER, BAR),
    # Bar 3: Bbmaj7
    ("A#", 2, WHOLE, BAR * 2),
    ("D", 3, WHOLE, BAR * 2),
    ("F", 3, WHOLE, BAR * 2),
    ("A#", 1, QUARTER, BAR * 2),
    # Bar 4: A7 tension
    ("A", 2, WHOLE, BAR * 3),
    ("C#", 3, WHOLE, BAR * 3),
    ("G", 3, WHOLE, BAR * 3),
    ("A", 1, QUARTER, BAR * 3),
]
for pitch, oct, dur, at in lh_chords:
    piano.add(Note(pitch, oct, dur, velocity=0.52), at=at)

# Right hand melody — starts at beat 0.5, sustained notes overlap the chords
rh_melody = [
    (0.5, "F", 5, DOTTED_QUARTER, 0.70),
    (2.0, "E", 5, QUARTER, 0.68),
    (2.5, "D", 5, HALF, 0.72),
    (BAR + 0.5, "G", 5, HALF, 0.65),
    (BAR + 2.0, "F", 5, QUARTER, 0.68),
    (BAR + 2.5, "E", 5, HALF, 0.70),
    (BAR * 2 + 0.0, "D", 5, HALF, 0.72),
    (BAR * 2 + 1.5, "C", 5, QUARTER, 0.65),
    (BAR * 2 + 2.5, "A#", 4, DOTTED_QUARTER, 0.68),
    (BAR * 3 + 0.0, "C#", 5, DOTTED_QUARTER, 0.75),
    (BAR * 3 + 1.5, "E", 5, QUARTER, 0.70),
    (BAR * 3 + 2.5, "A", 4, HALF, 0.65),
]
for at, pitch, oct, dur, vel in rh_melody:
    piano.add(Note(pitch, oct, dur, velocity=vel), at=at)

# Second phrase — repeat with variation
for pitch, oct, dur, at in lh_chords:
    piano.add(Note(pitch, oct, dur, velocity=0.48), at=at + BAR * 4)

for at, pitch, oct, dur, vel in rh_melody:
    # Harmonize right hand up a third for variation
    from code_music.engine import NOTE_NAMES, note_name_to_midi

    midi = note_name_to_midi(pitch, oct) + 5  # up a fourth
    new_pitch = NOTE_NAMES[midi % 12]
    new_oct = midi // 12 - 1
    piano.add(Note(new_pitch, new_oct, dur, velocity=vel * 0.85), at=at + BAR * 4)

# ── Contrabass — walking ──────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="contrabass", volume=0.70, pan=0.1, swing=0.48))
walk = humanize(
    [
        Note("D", 2, 1.0),
        Note("F", 2, 1.0),
        Note("A", 2, 1.0),
        Note("C", 3, 1.0),
        Note("G", 2, 1.0),
        Note("B", 2, 1.0),
        Note("D", 3, 1.0),
        Note("F", 3, 1.0),
        Note("A#", 1, 1.0),
        Note("D", 2, 1.0),
        Note("F", 2, 1.0),
        Note("A", 2, 1.0),
        Note("A", 1, 1.0),
        Note("C#", 2, 1.0),
        Note("E", 2, 1.0),
        Note("G", 2, 1.0),
    ]
    * 2,
    vel_spread=0.06,
    timing_spread=0.02,
)
bass.extend(walk)

# ── Brushed hi-hat ────────────────────────────────────────────────────────
ride = song.add_track(Track(name="ride", instrument="drums_ride", volume=0.30, swing=0.50))
for _ in range(8):
    ride.extend([Note("F", 5, EIGHTH, velocity=0.28)] * 8)

song.effects = {
    "piano": lambda s, sr: conv_reverb(
        delay(s, sr, delay_ms=338.0, feedback=0.22, wet=0.1),
        sr,
        room="chamber",
        wet=0.28,
    ),
    "bass": lambda s, sr: reverb(s, sr, room_size=0.4, wet=0.12),
}
