"""tank_bebop.py — inspired by "Tank!" (The Seatbelts / Yoko Kanno, Cowboy Bebop).

Original style: big-band jazz with aggressive drums, walking bass, punchy
brass unisons, bebop saxophone lines, and a swinging piano comping.
We cannot copy Tank! — this is original music in the same spirit.

Structure (168 BPM, Bb major / G minor, strong swing):
  Bars 1-2:    Intro drum break
  Bars 3-6:    Brass fanfare + bass enters
  Bars 7-10:   Sax melody over piano comp + walking bass
  Bars 11-14:  Brass hits, piano solo-ish
  Bars 15-18:  Full band tutti — everyone
  Bars 19-22:  Breakdown — sax solo fragment over bass + ride
  Bars 23-26:  Big finish — brass stabs, cymbal crashes
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    compress,
    delay,
    reverb,
)

song = Song(title="Tank Bebop", bpm=168)
r = Note.rest

SWING = 0.52

# ── Drum kit ──────────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.95))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.8))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.45, swing=SWING))
ride = song.add_track(Track(name="ride", instrument="drums_ride", volume=0.5, swing=SWING))
crash = song.add_track(Track(name="crash", instrument="drums_crash", volume=0.7))

k = Note("C", 2, 1.0)
s = Note("D", 3, 1.0)
h = Note("F", 5, 0.5)
rd = Note("F", 5, 0.5)

# Intro drum break (bars 1-2)
kick.extend([k, r(0.5), k, r(0.5), r(1.0), k, r(0.5), k, r(0.5)])
snare.extend([r(1.5), s, r(0.5), r(1.5), s, r(0.5)])
crash.add(Note("C", 5, 0.5))
crash.extend([r(7.5)])

# Main pattern (bars 3-26)
BARS = 24
kick_beat = [k, r(1.0), k, r(1.0)]
snare_beat = [r(1.0), s, r(1.0), s]
hat_beat = [h, h, h, h, h, h, h, h]
ride_beat = [rd, rd, r(0.5), rd, rd, r(0.5), rd, r(0.5)]  # jazz ride pattern

for _ in range(BARS):
    kick.extend(kick_beat)
    snare.extend(snare_beat)
    hat.extend(hat_beat)
    ride.extend(ride_beat)

# Final crash
crash.extend([r((BARS + 2) * 4.0 - 0.5)])
crash.add(Note("C", 5, 2.0, velocity=1.0))

# ── Walking bass ──────────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="contrabass", volume=0.85, swing=SWING))
# Intro: sparse
bass.extend([Note("G", 2, 1.0), r(1.0), Note("G", 2, 1.0), r(1.0)] * 2)

# Main walking (chord-locked chromatic walks)
walk_Bb = [Note("A#", 2, 1.0), Note("C", 3, 1.0), Note("D", 3, 1.0), Note("F", 3, 1.0)]
walk_Gm = [Note("G", 2, 1.0), Note("A", 2, 1.0), Note("A#", 2, 1.0), Note("D", 3, 1.0)]
walk_Cm = [Note("C", 3, 1.0), Note("D", 3, 1.0), Note("D#", 3, 1.0), Note("G", 3, 1.0)]
walk_F7 = [Note("F", 2, 1.0), Note("G", 2, 1.0), Note("A", 2, 1.0), Note("C", 3, 1.0)]

prog = walk_Bb + walk_Gm + walk_Cm + walk_F7  # one 4-bar cycle
for _ in range(6):
    bass.extend(prog)

# ── Brass fanfare (bars 3-6) ──────────────────────────────────────────────
for inst, oct, pan_v in [("trumpet", 4, -0.3), ("trombone", 3, 0.3), ("brass_section", 4, 0.0)]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=0.8, pan=pan_v, swing=SWING))
    # Bars 1-2: rest
    tr.extend([r(8.0)])
    # Fanfare (bars 3-6)
    fanfare = [
        Note("A#", oct, 0.5),
        Note("D", oct + 1 if inst == "trumpet" else oct, 0.5),
        Note("F", oct, 0.5),
        Note("A#", oct, 1.0),
        r(0.5),
        Note("G", oct, 0.5),
        Note("A#", oct, 0.5),
        Note("C", oct, 0.5),
        Note("F", oct, 1.0),
        r(0.5),
        Note("A#", oct, 0.5),
        Note("C", oct, 0.5),
        Note("D", oct, 0.5),
        Note("F", oct, 0.5),
        Note("A#", oct, 2.0),
    ]
    tr.extend(fanfare)
    # Bars 7-14: stabs
    stab_prog = [
        Chord("A#", "maj", 3 if inst != "trumpet" else 4, duration=0.5),
        r(0.5),
        Chord("F", "dom7", 3 if inst != "trumpet" else 4, duration=0.5),
        r(1.5),
        Chord("G", "min7", 3 if inst != "trumpet" else 4, duration=0.5),
        r(0.5),
        Chord("C", "dom7", 3 if inst != "trumpet" else 4, duration=0.5),
        r(1.5),
    ]
    for _ in range(2):
        tr.extend(stab_prog * 2)
    # Bars 15-18: full tutti
    tutti = [
        Note("A#", oct, 0.5),
        Note("C", oct, 0.25),
        Note("D", oct, 0.25),
        Note("F", oct, 0.5),
        Note("A#", oct, 0.5),
        Note("G", oct, 0.5),
        Note("F", oct, 0.5),
        Note("D", oct, 0.5),
        Note("C", oct, 0.5),
        Note("A#", oct, 2.0),
    ]
    tr.extend(tutti * 2)
    # Bars 19-22: rest
    tr.extend([r(16.0)])
    # Bars 23-26: big finish stabs
    finish = [
        Chord("A#", "maj", 4 if inst == "trumpet" else 3, duration=0.5),
        r(0.5),
        Chord("A#", "maj", 4 if inst == "trumpet" else 3, duration=0.5),
        r(0.5),
        Chord("F", "dom7", 4 if inst == "trumpet" else 3, duration=0.5),
        r(1.5),
        Chord("A#", "maj", 4 if inst == "trumpet" else 3, duration=4.0),
    ]
    tr.extend(finish)

# ── Piano comp ────────────────────────────────────────────────────────────
piano = song.add_track(Track(name="piano", instrument="rhodes", volume=0.6, swing=SWING, pan=0.1))
piano.extend([r(8.0)])  # rest during intro + fanfare
comp_loop = [
    Chord("A#", "maj7", 3, duration=2.0, velocity=0.65),
    Chord("G", "min7", 3, duration=2.0, velocity=0.6),
    Chord("C", "min7", 3, duration=2.0, velocity=0.6),
    Chord("F", "dom7", 3, duration=2.0, velocity=0.65),
]
for _ in range(4):
    piano.extend(comp_loop)
piano.extend([r(4.0)])  # breakdown
# Piano "solo" fragment
solo = [
    Note("A#", 4, 0.5),
    Note("D", 5, 0.5),
    Note("F", 5, 0.25),
    Note("A#", 5, 0.25),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("F", 5, 1.0),
    Note("D", 5, 0.25),
    Note("C", 5, 0.25),
    Note("A#", 4, 0.5),
    Note("G", 4, 0.5),
    Note("F", 4, 1.0),
    Note("A#", 4, 0.25),
    Note("C", 5, 0.25),
    Note("D", 5, 0.5),
    Note("F", 5, 0.5),
    Note("A#", 5, 2.0),
]
piano.extend(solo)
piano.extend([r(4.0)])

# ── Saxophone melody (bars 7-14, 19-22) ──────────────────────────────────
sax = song.add_track(Track(name="sax", instrument="saxophone", volume=0.75, swing=SWING, pan=-0.15))
sax.extend([r(24.0)])  # rest first 6 bars
# Bars 7-10: bebop melody in Bb
melody = [
    Note("A#", 4, 0.5),
    Note("D", 5, 0.5),
    Note("F", 5, 0.25),
    Note("A#", 5, 0.25),
    Note("G", 5, 0.5),
    Note("F", 5, 0.5),
    Note("D", 5, 1.0),
    Note("C", 5, 0.5),
    Note("D", 5, 0.25),
    Note("D#", 5, 0.25),
    Note("F", 5, 0.5),
    r(0.5),
    Note("A#", 4, 2.0),
]
sax.extend(melody * 2)
# Bars 11-14: response phrase
response = [
    r(0.5),
    Note("G", 4, 0.5),
    Note("A", 4, 0.25),
    Note("A#", 4, 0.25),
    Note("C", 5, 0.5),
    Note("A#", 4, 0.5),
    Note("G", 4, 1.0),
    Note("F", 4, 0.5),
    Note("G", 4, 0.25),
    Note("A#", 4, 0.25),
    Note("C", 5, 0.5),
    r(0.5),
    Note("F", 4, 2.0),
]
sax.extend(response * 2)
# Bars 15-18: rest (brass tutti)
sax.extend([r(16.0)])
# Bars 19-22: solo fragment
sax.extend(melody)
sax.extend(response)
# Bars 23-26: rest
sax.extend([r(16.0)])

# ── Effects ───────────────────────────────────────────────────────────────
song._effects = {
    "bass": lambda s, sr: compress(s, sr, threshold=0.6, ratio=3.0, makeup_gain=1.1),
    "sax": lambda s, sr: reverb(s, sr, room_size=0.35, wet=0.12),
    "piano": lambda s, sr: reverb(s, sr, room_size=0.3, wet=0.1),
    "trumpet": lambda s, sr: delay(s, sr, delay_ms=45.0, feedback=0.15, wet=0.08),
}
