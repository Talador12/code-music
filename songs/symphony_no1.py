"""symphony_no1.py — A short original symphony movement in C minor.

Structure: Sonata form (fast movement), 4/4 at 108 BPM.

  Exposition (bars 1-12):
    Bars 1-4:   1st Theme — strings unison, dramatic C minor
    Bars 5-8:   Development of 1st theme — woodwinds enter
    Bars 9-12:  2nd Theme — Eb major, lyrical strings + oboe

  Development (bars 13-20):
    Bars 13-16: Modulation — brass take over, rising sequence
    Bars 17-20: Climax — full orchestra, timpani, ff dynamics

  Recapitulation (bars 21-28):
    Bars 21-24: 1st Theme returns — full strings + brass
    Bars 25-28: Coda — final resolution to C major

Techniques:
  - crescendo()/decrescendo() on note sequences
  - transpose() for modulations
  - humanize() on strings for organic feel
  - Full orchestral sections: strings, brass, woodwinds, timpani
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    crescendo,
    decrescendo,
    humanize,
    reverb,
    transpose,
)

song = Song(title="Symphony No. 1", bpm=108)
r = Note.rest

# ── Theme material ─────────────────────────────────────────────────────────
# 1st theme: dramatic, unison, C minor
theme_1 = [
    Note("C", 4, 0.5),
    Note("C", 4, 0.5),
    Note("D#", 4, 0.5),
    Note("G", 4, 0.5),
    Note("G", 4, 1.0),
    Note("F", 4, 0.5),
    Note("D#", 4, 0.5),
    Note("D", 4, 1.0),
    r(1.0),
    Note("C", 4, 0.5),
    Note("D", 4, 0.25),
    Note("D#", 4, 0.25),
    Note("F", 4, 0.5),
    Note("G", 4, 0.5),
    Note("A#", 4, 1.0),
    Note("G", 4, 4.0),
]

# 2nd theme: lyrical, Eb major
theme_2 = [
    Note("D#", 4, 1.0),
    Note("F", 4, 0.5),
    Note("G", 4, 0.5),
    Note("A#", 4, 2.0),
    Note("G", 4, 1.0),
    r(1.0),
    Note("G", 4, 0.5),
    Note("A#", 4, 0.5),
    Note("C", 5, 0.5),
    Note("D#", 5, 0.5),
    Note("D#", 5, 2.0),
    Note("C", 5, 1.0),
    r(1.0),
]

# Climax theme: fff energy, rising
climax = crescendo(
    [
        Note("C", 5, 0.5),
        Note("D", 5, 0.5),
        Note("D#", 5, 0.5),
        Note("F", 5, 0.5),
        Note("G", 5, 1.0),
        Note("A#", 5, 0.5),
        Note("C", 6, 0.5),
        Note("C", 6, 2.0),
        Note("A#", 5, 0.5),
        Note("G", 5, 0.5),
        Note("F", 5, 0.5),
        Note("D#", 5, 0.5),
        Note("C", 5, 2.0),
        Note("G", 4, 0.5),
        Note("A#", 4, 0.5),
        Note("C", 5, 1.0),
        Note("C", 5, 4.0),
    ],
    start_vel=0.5,
    end_vel=1.0,
)

# Coda: decrescendo to peace in C major
coda = decrescendo(
    [
        Note("C", 4, 1.0),
        Note("E", 4, 1.0),
        Note("G", 4, 1.0),
        Note("C", 5, 1.0),
        Note("G", 4, 1.0),
        Note("E", 4, 1.0),
        Note("C", 4, 2.0),
        Note("E", 4, 1.0),
        Note("G", 4, 1.0),
        Note("C", 5, 4.0),
        Note("C", 4, 4.0),
    ],
    start_vel=0.9,
    end_vel=0.2,
)

# ── Violin I — melody lead ─────────────────────────────────────────────────
vln1 = song.add_track(Track(name="vln1", instrument="violin", volume=0.72, pan=-0.35))
# Exposition
vln1.extend(humanize(crescendo(theme_1, 0.4, 0.85), vel_spread=0.05))
vln1.extend(
    humanize(theme_1[:8] + [Note("D#", 4, 1.0), Note("F", 4, 1.0), r(2.0)], vel_spread=0.04)
)
vln1.extend(
    humanize(
        [
            Note("D#", 4, d, v)
            for d, v in zip(
                [1, 0.5, 0.5, 1, 1, 0.5, 0.5, 1], [0.55, 0.6, 0.65, 0.7, 0.65, 0.7, 0.75, 0.65]
            )
        ]
        + list(theme_2[-8:]),
        vel_spread=0.04,
    )
)
# Development
dev_theme = transpose(theme_1, 3)  # modulate up a minor third
vln1.extend(crescendo(dev_theme[:8], 0.5, 0.75))
vln1.extend(crescendo(transpose(theme_1, 7)[:8], 0.6, 0.9))  # up a fifth
vln1.extend(humanize(climax[:8], vel_spread=0.03))
vln1.extend(climax[8:])
# Recapitulation
vln1.extend(crescendo(theme_1, 0.7, 1.0))
vln1.extend(coda)

# ── Violin II — harmony ────────────────────────────────────────────────────
vln2 = song.add_track(Track(name="vln2", instrument="violin", volume=0.65, pan=-0.15))
harm = transpose(theme_1, -7)  # harmonize a fifth below
vln2.extend(humanize(crescendo(harm, 0.35, 0.75), vel_spread=0.06))
vln2.extend(humanize(harm[:8] + [Note("C", 4, 4.0)], vel_spread=0.05))
# 2nd theme harmony
vln2.extend(humanize(transpose(theme_2, -4), vel_spread=0.04))
# Development
vln2.extend(crescendo(transpose(harm, 3), 0.4, 0.7))
vln2.extend(crescendo(transpose(harm, 7), 0.5, 0.85))
vln2.extend(transpose(climax, -4))
# Recap
vln2.extend(crescendo(harm, 0.65, 0.95))
vln2.extend(decrescendo(transpose(coda, -4), 0.85, 0.15))

# ── Cello ─────────────────────────────────────────────────────────────────
vc = song.add_track(Track(name="cello", instrument="cello", volume=0.7, pan=0.3))
bass_line_exp = crescendo(
    [
        Note("C", 3, 4.0),
        Note("G", 2, 4.0),
        Note("D#", 3, 4.0),
        Note("G", 2, 4.0),
        Note("C", 3, 2.0),
        Note("G", 2, 2.0),
        Note("F", 2, 2.0),
        Note("G", 2, 2.0),
    ],
    0.4,
    0.8,
)
vc.extend(bass_line_exp)
# 2nd theme: Eb bass
vc.extend(
    [
        Note("D#", 3, 4.0),
        Note("A#", 2, 4.0),
        Note("D#", 3, 2.0),
        Note("A#", 2, 2.0),
        Note("G", 2, 2.0),
        Note("C", 3, 2.0),
    ]
)
# Development: rising line
vc.extend(
    crescendo(
        [
            Note("C", 3, 2.0),
            Note("D#", 3, 2.0),
            Note("F", 3, 2.0),
            Note("G", 3, 2.0),
            Note("G#", 3, 2.0),
            Note("A#", 3, 2.0),
            Note("C", 4, 2.0),
            Note("G", 3, 2.0),
        ],
        0.5,
        1.0,
    )
)
# Recap
vc.extend(bass_line_exp)
vc.extend(
    decrescendo(
        [
            Note("C", 3, 2.0),
            Note("G", 2, 2.0),
            Note("E", 2, 2.0),
            Note("C", 2, 4.0),
            Note("G", 2, 2.0),
            Note("C", 3, 6.0),
        ],
        0.9,
        0.1,
    )
)

# ── Contrabass ────────────────────────────────────────────────────────────
cb = song.add_track(Track(name="cb", instrument="contrabass", volume=0.65, pan=0.45))
cb_line = crescendo(
    [
        Note("C", 2, 4.0),
        Note("G", 1, 4.0),
        Note("D#", 2, 4.0),
        Note("G", 1, 4.0),
        Note("C", 2, 4.0),
        Note("G", 1, 4.0),
    ],
    0.4,
    0.8,
)
cb.extend(cb_line)
cb.extend([Note("D#", 2, 4.0), Note("A#", 1, 4.0), Note("D#", 2, 2.0), Note("G", 1, 2.0)])
cb.extend(
    crescendo(
        [
            Note("C", 2, 2.0),
            Note("D#", 2, 2.0),
            Note("F", 2, 2.0),
            Note("G", 2, 2.0),
            Note("G#", 2, 2.0),
            Note("A#", 2, 2.0),
            Note("C", 3, 2.0),
            Note("G", 2, 2.0),
        ],
        0.5,
        1.0,
    )
)
cb.extend(cb_line)
cb.extend(
    decrescendo(
        [
            Note("C", 2, 2.0),
            Note("G", 1, 2.0),
            Note("E", 1, 2.0),
            Note("C", 1, 4.0),
            Note("G", 1, 2.0),
            Note("C", 2, 6.0),
        ],
        0.9,
        0.1,
    )
)

# ── Oboe — 2nd theme + development ────────────────────────────────────────
oboe = song.add_track(Track(name="oboe", instrument="oboe", volume=0.65, pan=0.0))
oboe.extend([r(16.0)])  # silent first 4 bars exposition
# Bars 5-8: counter-melody
oboe.extend(
    humanize(
        [
            Note("G", 5, 1.0),
            Note("F", 5, 0.5),
            Note("D#", 5, 0.5),
            Note("D", 5, 2.0),
            r(2.0),
            Note("D#", 5, 1.0),
            Note("F", 5, 0.5),
            Note("G", 5, 0.5),
            Note("A#", 5, 2.0),
            r(2.0),
        ],
        vel_spread=0.04,
    )
)
# 2nd theme (oboe = main voice)
oboe.extend(humanize(transpose(theme_2, 12), vel_spread=0.04))
# Development + climax
oboe.extend(crescendo(transpose(theme_2, 12 + 3)[:8], 0.5, 0.9))
oboe.extend(crescendo(transpose(theme_2, 12 + 7)[:8], 0.6, 1.0))
oboe.extend([r(8.0)])  # climax — brass take over
# Recap
oboe.extend(humanize(transpose(theme_2, 12), vel_spread=0.03))
oboe.extend([r(12.0)])

# ── Clarinet — fills ──────────────────────────────────────────────────────
clar = song.add_track(Track(name="clarinet", instrument="clarinet", volume=0.6, pan=-0.1))
clar.extend([r(8.0)])
clar.extend(
    humanize(
        [
            Note("D#", 5, 0.5),
            Note("F", 5, 0.5),
            Note("G", 5, 0.5),
            Note("A#", 5, 0.5),
            Note("G", 5, 2.0),
            r(2.0),
            Note("F", 5, 0.5),
            Note("G", 5, 0.5),
            Note("A#", 5, 1.0),
            Note("C", 6, 1.0),
            r(1.0),
            Note("D#", 5, 4.0),
        ],
        vel_spread=0.05,
    )
)
clar.extend([r(4.0)])  # 2nd theme
clar.extend([r(8.0)])  # development silence
clar.extend(
    crescendo(
        [
            Note("C", 5, 1.0),
            Note("D", 5, 1.0),
            Note("D#", 5, 1.0),
            Note("G", 5, 1.0),
            Note("A#", 5, 2.0),
            Note("G", 5, 2.0),
            Note("F", 5, 2.0),
            Note("D#", 5, 2.0),
        ],
        0.5,
        0.95,
    )
)
clar.extend([r(16.0)])

# ── French horn — pads + fanfare ──────────────────────────────────────────
horn = song.add_track(Track(name="horn", instrument="french_horn", volume=0.7, pan=0.2))
# Exposition: sustained chords
for _ in range(3):
    horn.add(Chord("C", "min", 3, duration=4.0, velocity=0.5))
    horn.add(Chord("G", "min", 3, duration=4.0, velocity=0.5))
    horn.add(Chord("D#", "maj", 3, duration=4.0, velocity=0.55))
    horn.add(Chord("G", "dom7", 3, duration=4.0, velocity=0.5))
# Development: rising fanfare
horn.extend(
    crescendo(
        [
            Note("G", 3, 1.0),
            Note("A#", 3, 1.0),
            Note("C", 4, 1.0),
            Note("D#", 4, 1.0),
            Note("D#", 4, 2.0),
            Note("C", 4, 2.0),
            Note("G", 3, 1.0),
            Note("A#", 3, 1.0),
            Note("D#", 4, 2.0),
            r(2.0),
        ],
        0.5,
        0.95,
    )
)
# Recap + coda
for _ in range(2):
    horn.add(Chord("C", "min", 3, duration=4.0, velocity=0.7))
    horn.add(Chord("G", "min", 3, duration=4.0, velocity=0.7))
horn.extend(
    decrescendo(
        [
            Chord("C", "maj", 3, duration=4.0, velocity=0.8),
            Chord("G", "dom7", 3, duration=4.0, velocity=0.6),
            Chord("C", "maj", 3, duration=8.0, velocity=0.4),
        ],
        0.8,
        0.15,
    )
)

# ── Trumpet — development + climax ────────────────────────────────────────
tpt = song.add_track(Track(name="trumpet", instrument="trumpet", volume=0.75, pan=-0.2))
tpt.extend([r(32.0)])  # rest until development
tpt.extend(
    crescendo(
        [
            Note("C", 5, 0.5),
            Note("D#", 5, 0.5),
            Note("G", 5, 0.5),
            Note("C", 6, 0.5),
            Note("C", 6, 2.0),
            r(2.0),
            Note("A#", 5, 0.5),
            Note("G", 5, 0.5),
            Note("F", 5, 0.5),
            Note("D#", 5, 0.5),
            Note("C", 5, 2.0),
            r(2.0),
            Note("C", 5, 0.5),
            Note("F", 5, 0.25),
            Note("G", 5, 0.25),
            Note("A#", 5, 0.5),
            Note("C", 6, 1.0),
            Note("D#", 6, 1.0),
            Note("C", 6, 4.0),
        ],
        0.6,
        1.0,
    )
)
tpt.extend([r(32.0)])

# ── Timpani ────────────────────────────────────────────────────────────────
timp = song.add_track(Track(name="timp", instrument="timpani", volume=0.9))
# Sparse in exposition
timp.extend(
    [r(4.0), Note("G", 2, 0.25)] * 2 + [r(3.5)] + [r(4.0), Note("C", 2, 0.25)] * 2 + [r(3.5)]
)
timp.extend([r(16.0)])  # 2nd theme: silent
# Development: rolls
for pitch in ["C", "D#", "F", "G", "G", "A#", "C"]:
    timp.extend([Note(pitch, 2, 0.25)] * 8)
# Recap
timp.extend([r(4.0), Note("C", 2, 0.5), Note("G", 2, 0.25), r(3.25)] * 4)
# Coda: final hits
timp.extend(
    [
        r(8.0),
        Note("C", 2, 1.0, velocity=0.8),
        r(3.0),
        Note("G", 2, 0.5, velocity=0.6),
        r(3.5),
        Note("C", 2, 4.0, velocity=0.9),
    ]
)

# ── Effects ────────────────────────────────────────────────────────────────
song._effects = {
    "vln1": lambda s, sr: reverb(s, sr, room_size=0.75, damping=0.4, wet=0.25),
    "vln2": lambda s, sr: reverb(s, sr, room_size=0.75, damping=0.4, wet=0.25),
    "cello": lambda s, sr: reverb(s, sr, room_size=0.8, damping=0.35, wet=0.28),
    "cb": lambda s, sr: reverb(s, sr, room_size=0.8, damping=0.35, wet=0.28),
    "oboe": lambda s, sr: reverb(s, sr, room_size=0.7, wet=0.2),
    "clarinet": lambda s, sr: reverb(s, sr, room_size=0.7, wet=0.2),
    "horn": lambda s, sr: reverb(s, sr, room_size=0.85, wet=0.3),
    "trumpet": lambda s, sr: reverb(s, sr, room_size=0.85, wet=0.25),
    "timp": lambda s, sr: reverb(s, sr, room_size=0.9, wet=0.35),
}
