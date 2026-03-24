"""after_midnight.py — Jazz ballad. Dm, 58 BPM. Third track for After Hours album.

Slower than tank_bebop, more introspective than lo_fi_loop. The space
that happens at 2am in a jazz club when everyone's tired and the
musicians stop showing off and start playing. Trumpet with a lot of
space. Piano that comps quietly. Bass that holds everything together.
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
    delay,
    humanize,
    reverb,
)

song = Song(title="After Midnight", bpm=58)

BAR = 4.0
SWING = 0.5
r = Note.rest

# ── Piano comp — shell voicings, space ───────────────────────────────────
comp = song.add_track(Track(name="comp", instrument="rhodes", volume=0.52, pan=-0.2, swing=SWING))
changes = [
    Chord("D", "min7", 3, duration=BAR * 2, velocity=0.48),
    Chord("G", "dom7", 3, duration=BAR * 2, velocity=0.45),
    Chord("C", "maj7", 3, duration=BAR * 2, velocity=0.48),
    Chord("A", "dom7", 3, duration=BAR * 2, velocity=0.5),
    Chord("D", "min9", 3, duration=BAR * 2, velocity=0.47),
    Chord("E", "min7b5", 3, duration=BAR * 2, velocity=0.45),
    Chord("A", "dom7", 3, duration=BAR * 2, velocity=0.5),
    Chord("D", "min7", 3, duration=BAR * 4, velocity=0.45),
]
for _ in range(2):
    comp.extend(changes)

# ── Walking contrabass ────────────────────────────────────────────────────
bass = song.add_track(
    Track(name="bass", instrument="contrabass", volume=0.72, pan=0.1, swing=SWING)
)
walk = humanize(
    [
        Note("D", 2, 1.0),
        Note("F", 2, 1.0),
        Note("A", 2, 1.0),
        Note("C", 3, 1.0),
        Note("G", 1, 1.0),
        Note("B", 1, 1.0),
        Note("D", 2, 1.0),
        Note("F", 2, 1.0),
        Note("C", 2, 1.0),
        Note("E", 2, 1.0),
        Note("G", 2, 1.0),
        Note("B", 2, 1.0),
        Note("A", 1, 1.0),
        Note("C#", 2, 1.0),
        Note("E", 2, 1.0),
        Note("G#", 2, 1.0),
        Note("D", 2, 1.0),
        Note("F", 2, 1.0),
        Note("A", 2, 1.0),
        Note("E", 3, 1.0),
        Note("E", 2, 1.0),
        Note("G", 2, 1.0),
        Note("B", 2, 1.0),
        Note("D", 3, 1.0),
        Note("A", 1, 1.0),
        Note("C#", 2, 1.0),
        Note("E", 2, 1.0),
        Note("G", 2, 1.0),
        Note("D", 2, 4.0),
    ]
    * 2,
    vel_spread=0.06,
    timing_spread=0.02,
)
bass.extend(walk)

# ── Ride cymbal — jazz time, very light ──────────────────────────────────
ride = song.add_track(Track(name="ride", instrument="drums_ride", volume=0.35, swing=SWING))
ride_pat = [
    Note("F", 5, QUARTER, velocity=0.38),
    Note("F", 5, EIGHTH, velocity=0.28),
    Note("F", 5, EIGHTH, velocity=0.35),
] * 4
for _ in range(16):
    ride.extend(ride_pat)

# ── Trumpet solo — the whole reason for the song ─────────────────────────
tpt = song.add_track(
    Track(name="trumpet", instrument="trumpet", volume=0.68, pan=0.05, swing=SWING)
)
tpt.extend([r(BAR)] * 4)  # listen to the piano first

# The solo: mostly silence, notes chosen carefully
solo = humanize(
    [
        r(DOTTED_QUARTER),
        Note("A", 4, EIGHTH),
        r(QUARTER),
        Note("D", 5, HALF),
        r(HALF),
        r(BAR),
        Note("C", 5, QUARTER),
        Note("A", 4, EIGHTH),
        r(EIGHTH),
        Note("G", 4, HALF),
        r(BAR),
        r(QUARTER),
        Note("F", 4, DOTTED_QUARTER),
        Note("G", 4, EIGHTH),
        Note("A", 4, HALF),
        r(HALF),
        Note("D", 5, HALF),
        r(QUARTER),
        Note("C", 5, QUARTER),
        Note("A", 4, WHOLE),
        r(BAR),
        r(HALF),
        Note("E", 4, QUARTER),
        Note("F", 4, QUARTER),
        Note("G", 4, HALF),
        Note("A", 4, HALF),
        Note("D", 4, WHOLE),
        r(BAR),
        r(QUARTER),
        Note("A", 4, QUARTER),
        Note("C", 5, HALF),
        Note("D", 5, DOTTED_QUARTER),
        Note("C", 5, EIGHTH),
        Note("A", 4, HALF),
        r(HALF),
        Note("G", 4, WHOLE),
        r(BAR * 2),
    ],
    vel_spread=0.08,
    timing_spread=0.07,
)
tpt.extend(solo)

song._effects = {
    "trumpet": lambda s, sr: delay(
        reverb(s, sr, room_size=0.42, wet=0.18),
        sr,
        delay_ms=310.0,
        feedback=0.2,
        wet=0.1,
    ),
    "comp": lambda s, sr: chorus(reverb(s, sr, room_size=0.4, wet=0.12), sr, rate_hz=0.4, wet=0.1),
    "bass": lambda s, sr: reverb(s, sr, room_size=0.38, wet=0.1),
}
