"""second_chorus.py — Pop. C major, 116 BPM. suggest_progression-built.

Pop's job: make you feel something specific in under 3 minutes and bring
you back for it. I V vi IV is the four-chord universe — the Axis of Awesome.
What separates great pop from mediocre pop isn't the chords, it's the
melody sitting on top. This is a second pop track using suggest_progression().
"""

from code_music import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    WHOLE,
    Chord,
    Note,
    Song,
    Track,
    compress,
    crescendo,
    delay,
    generate_melody,
    reverb,
    stereo_width,
    suggest_progression,
)

song = Song(title="Second Chorus", bpm=116)

BAR = 4.0
r = Note.rest

# Progression from suggest_progression — happy mood, C major
PROG = suggest_progression("C", mood="happy", octave=3, duration=BAR, velocity=0.62)

# ── Pad — wide, behind everything ─────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.38, pan=0.0))
for _ in range(8):
    pad.extend(PROG)

# ── Piano comp — rhythmic, bright ────────────────────────────────────────
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.72, pan=-0.1))
piano_pat = [
    Chord("C", "maj", 3, duration=QUARTER, velocity=0.7),
    r(EIGHTH),
    Chord("C", "maj", 3, duration=EIGHTH, velocity=0.62),
    r(QUARTER),
    Chord("G", "maj", 3, duration=QUARTER, velocity=0.68),
    r(QUARTER),
    Chord("A", "min", 3, duration=QUARTER, velocity=0.65),
    r(EIGHTH),
    Chord("A", "min", 3, duration=EIGHTH, velocity=0.6),
    r(QUARTER),
    Chord("F", "maj", 3, duration=QUARTER, velocity=0.68),
    r(QUARTER),
]
for _ in range(8):
    piano.extend(piano_pat)

# ── Bass — root + 5th movement ────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.75))
bass_line = [
    Note("C", 2, 1.0),
    Note("C", 2, 0.5),
    Note("G", 2, 0.5),
    Note("G", 2, 1.0),
    Note("G", 2, 0.5),
    Note("D", 3, 0.5),
    Note("A", 2, 1.0),
    Note("A", 2, 0.5),
    Note("E", 3, 0.5),
    Note("F", 2, 1.0),
    Note("F", 2, 0.5),
    Note("C", 3, 0.5),
]
for _ in range(8):
    bass.extend(bass_line)

# ── Drums — straight, energetic ───────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.95))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.80))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.42))
crash = song.add_track(Track(name="crash", instrument="drums_crash", volume=0.7))

crash.add(Note("C", 5, 0.5, velocity=0.9))
crash.extend([r(BAR)] * 7 + [Note("C", 5, 0.5, velocity=0.75)] + [r(BAR)] * 7)

for _ in range(8):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])
    hat.extend([Note("F", 5, EIGHTH)] * 8)

# ── Lead melody — generated, then hand-tuned ──────────────────────────────
lead = song.add_track(Track(name="lead", instrument="piano", volume=0.78, pan=0.15))
# Verse: generated pentatonic
lead.extend([r(BAR)] * 2)
verse_mel = generate_melody("C", scale_mode="pentatonic", octave=5, bars=4, density=0.68, seed=7)
lead.extend(verse_mel)

# Chorus: hand-written anthem
chorus_mel = crescendo(
    [
        Note("G", 5, DOTTED_QUARTER),
        Note("A", 5, EIGHTH),
        Note("G", 5, HALF),
        Note("E", 5, QUARTER),
        Note("F", 5, QUARTER),
        Note("G", 5, HALF),
        Note("C", 6, DOTTED_QUARTER),
        Note("B", 5, EIGHTH),
        Note("A", 5, HALF),
        Note("G", 5, WHOLE),
        Note("A", 5, DOTTED_QUARTER),
        Note("B", 5, EIGHTH),
        Note("C", 6, HALF),
        Note("B", 5, QUARTER),
        Note("A", 5, QUARTER),
        Note("G", 5, HALF),
        Note("E", 5, QUARTER),
        Note("D", 5, QUARTER),
        Note("E", 5, QUARTER),
        Note("G", 5, QUARTER),
        Note("C", 5, WHOLE),
    ],
    start_vel=0.75,
    end_vel=0.95,
)
lead.extend(chorus_mel)
lead.extend([r(BAR)] * 2)
lead.extend(chorus_mel)

song._effects = {
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.6, wet=0.25), width=1.6),
    "lead": lambda s, sr: delay(s, sr, delay_ms=258.0, feedback=0.25, wet=0.12, ping_pong=False),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
}
