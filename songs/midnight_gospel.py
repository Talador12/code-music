"""midnight_gospel.py — Gospel/Soul. Bb major, 82 BPM. Second gospel track.

Where gospel_hour.py is a full SATB choir production, this one is
more intimate — a late-night session, voices tired but committed.
Bb major gospel is the church key par excellence.
Rhodes, walking bass, choir, and a piano that knows when to stay out of the way.
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
    chorus,
    compress,
    crescendo,
    decrescendo,
    humanize,
    reverb,
    stereo_width,
)

song = Song(title="Midnight Gospel", bpm=82)

BAR = 4.0
SWING = 0.48
r = Note.rest

# ── Gospel chord progression: I - IV - I - V in Bb ────────────────────────
prog = [
    Chord("A#", "maj7", 3, duration=BAR * 2, velocity=0.6),
    Chord("D#", "maj7", 3, duration=BAR * 2, velocity=0.58),
    Chord("A#", "maj7", 3, duration=BAR * 2, velocity=0.6),
    Chord("F", "dom7", 3, duration=BAR * 2, velocity=0.62),
]

# ── Organ — the foundation ────────────────────────────────────────────────
organ = song.add_track(Track(name="organ", instrument="organ", volume=0.48, swing=SWING))
for _ in range(4):
    organ.extend(prog)

# ── Rhodes fills ──────────────────────────────────────────────────────────
piano = song.add_track(
    Track(name="piano", instrument="rhodes", volume=0.62, swing=SWING, pan=-0.15)
)
fills = [
    Chord("A#", "maj", 3, duration=QUARTER, velocity=0.72),
    r(QUARTER),
    r(HALF),
    Chord("A#", "maj", 3, duration=EIGHTH, velocity=0.68),
    r(EIGHTH),
    r(HALF),
    Chord("D#", "maj", 3, duration=QUARTER, velocity=0.70),
    r(QUARTER),
    r(HALF),
    r(QUARTER),
    Chord("D#", "maj", 3, duration=QUARTER, velocity=0.65),
    r(HALF),
    Chord("A#", "maj", 3, duration=QUARTER, velocity=0.72),
    r(QUARTER),
    Chord("A#", "maj", 3, duration=EIGHTH, velocity=0.65),
    r(EIGHTH),
    r(HALF),
    Chord("F", "dom7", 3, duration=QUARTER, velocity=0.75),
    r(QUARTER),
    r(HALF),
    Chord("F", "dom7", 3, duration=EIGHTH, velocity=0.70),
    r(EIGHTH),
    Chord("A#", "maj", 3, duration=QUARTER, velocity=0.72),
    r(HALF + QUARTER),
]
for _ in range(4):
    piano.extend(fills)

# ── Walking bass ──────────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="contrabass", volume=0.75, swing=SWING))
walk = humanize(
    [
        Note("A#", 2, 1.0),
        Note("C", 3, 1.0),
        Note("D", 3, 1.0),
        Note("F", 3, 1.0),
        Note("D#", 2, 1.0),
        Note("F", 2, 1.0),
        Note("G", 2, 1.0),
        Note("A#", 2, 1.0),
        Note("A#", 2, 1.0),
        Note("C", 3, 1.0),
        Note("D", 3, 1.0),
        Note("F", 3, 1.0),
        Note("F", 2, 1.0),
        Note("G", 2, 1.0),
        Note("A", 2, 1.0),
        Note("C", 3, 1.0),
    ],
    vel_spread=0.06,
    timing_spread=0.02,
)
for _ in range(4):
    bass.extend(walk * 2)

# ── Choir — call and response ─────────────────────────────────────────────
choir = song.add_track(
    Track(name="choir", instrument="choir_aah", volume=0.6, pan=0.05, swing=SWING)
)
choir.extend([r(BAR)] * 8)  # wait for the groove to establish

call = crescendo(
    [
        Note("A#", 5, DOTTED_QUARTER),
        Note("C", 6, EIGHTH),
        Note("D#", 6, HALF),
        Note("F", 6, QUARTER),
        Note("D#", 6, QUARTER),
        Note("C", 6, WHOLE),
        r(HALF),
        Note("D#", 5, HALF),
        Note("F", 5, QUARTER),
        Note("D#", 5, QUARTER),
        Note("A#", 4, WHOLE),
    ],
    0.4,
    0.92,
)

response = decrescendo(
    [
        Note("D#", 5, QUARTER),
        Note("F", 5, QUARTER),
        Note("G", 5, HALF),
        Note("F", 5, QUARTER),
        Note("D#", 5, QUARTER),
        Note("C", 5, WHOLE),
        r(BAR),
    ],
    0.88,
    0.3,
)

choir.extend(humanize(call + response, vel_spread=0.05))
choir.extend(humanize(call + response, vel_spread=0.05))
choir.extend(humanize(crescendo(call, 0.7, 1.0) + decrescendo(response, 0.9, 0.2), vel_spread=0.04))

# ── Kit ───────────────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.85))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.75, swing=SWING))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35, swing=SWING))

for _ in range(16):
    kick.extend([Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5), r(1.0), Note("C", 2, 1.0)])
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])
    hat.extend([Note("F", 5, 0.5)] * 8)

song._effects = {
    "choir": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.88, wet=0.45), width=1.6),
    "organ": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.65, wet=0.25), sr, rate_hz=0.3, wet=0.12
    ),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
}
