"""open_circuit.py — Ambient / Cinematic. Third Carrier album track.

Different mood from deep_space_drift and cinematic_rise. More tonal,
more structured. Eb major / Dorian, 65 BPM. Piano carries a real melody
this time — not generative, but written. Strings answer. No drums.
Think Nils Frahm meets Jon Hopkins.
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
    crescendo,
    decrescendo,
    delay,
    humanize,
    reverb,
    stereo_width,
)

song = Song(title="Open Circuit", bpm=65)

BAR = 4.0
r = Note.rest

# ── Pad — Eb Dorian, very wide ────────────────────────────────────────────
pad_l = song.add_track(Track(name="pad_l", instrument="pad", volume=0.4, pan=-0.5))
pad_r = song.add_track(Track(name="pad_r", instrument="pad", volume=0.4, pan=0.5))
for ch, sh, dur in [
    ("D#", "min7", 8.0),
    ("C", "maj7", 8.0),
    ("G#", "maj7", 8.0),
    ("A#", "dom7", 8.0),
    ("D#", "min7", 16.0),
    ("G#", "maj7", 8.0),
    ("A#", "dom7", 4.0),
    ("D#", "min", 4.0),
]:
    for pad in (pad_l, pad_r):
        pad.add(Chord(ch, sh, 3, duration=dur, velocity=0.45))

# ── Piano — the heart of the piece ───────────────────────────────────────
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.72, pan=-0.05))

phrase_a = humanize(
    crescendo(
        [
            Note("D#", 5, DOTTED_QUARTER),
            Note("F", 5, EIGHTH),
            Note("G#", 5, HALF),
            Note("G", 5, QUARTER),
            Note("F", 5, QUARTER),
            Note("D#", 5, HALF),
            r(HALF),
            Note("C", 5, DOTTED_QUARTER),
            Note("D#", 5, EIGHTH),
            Note("F", 5, HALF),
            Note("D#", 5, QUARTER),
            Note("C", 5, QUARTER),
            Note("G#", 4, WHOLE),
        ],
        0.3,
        0.82,
    ),
    vel_spread=0.07,
    timing_spread=0.04,
)

phrase_b = humanize(
    decrescendo(
        [
            Note("A#", 5, HALF),
            Note("G#", 5, QUARTER),
            Note("G", 5, QUARTER),
            Note("F", 5, HALF),
            Note("D#", 5, WHOLE),
            Note("C", 5, DOTTED_QUARTER),
            Note("A#", 4, EIGHTH),
            Note("G#", 4, HALF),
            Note("F", 4, QUARTER),
            Note("G", 4, QUARTER),
            Note("D#", 4, WHOLE),
        ],
        0.85,
        0.2,
    ),
    vel_spread=0.07,
    timing_spread=0.04,
)

piano.extend(phrase_a)
piano.extend(phrase_b)
piano.extend(humanize(crescendo(phrase_a, 0.35, 0.9), vel_spread=0.05))
piano.extend(phrase_b)

# ── Strings — enter after first phrase ───────────────────────────────────
for inst, pan_v, vol in [("violin", -0.3, 0.55), ("strings", 0.2, 0.5), ("cello", 0.35, 0.58)]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=vol, pan=pan_v))
    tr.extend([r(BAR)] * 8)
    tr.extend(
        crescendo(
            [
                Note("D#", 4 if inst != "cello" else 3, 4.0, velocity=0.4),
                Note("C", 4 if inst != "cello" else 3, 4.0, velocity=0.42),
                Note("G#", 3 if inst != "cello" else 2, 4.0, velocity=0.45),
                Note("A#", 3 if inst != "cello" else 2, 4.0, velocity=0.48),
                Note("D#", 4 if inst != "cello" else 3, 8.0, velocity=0.5),
                Note("G#", 3 if inst != "cello" else 2, 8.0, velocity=0.45),
            ],
            0.25,
            0.72,
        )
    )

song._effects = {
    "pad_l": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.88, wet=0.45), width=1.8),
    "pad_r": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.88, wet=0.45), width=1.8),
    "piano": lambda s, sr: delay(
        reverb(s, sr, room_size=0.7, wet=0.3), sr, delay_ms=923.0, feedback=0.38, wet=0.22
    ),
    "violin": lambda s, sr: reverb(s, sr, room_size=0.85, wet=0.32),
    "strings": lambda s, sr: reverb(s, sr, room_size=0.85, wet=0.3),
    "cello": lambda s, sr: reverb(s, sr, room_size=0.85, wet=0.32),
}
