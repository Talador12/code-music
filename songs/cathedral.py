"""cathedral.py — Classical. Full orchestra, Romantic era, Cm, 84 BPM.

A second orchestral movement — slower, more emotional than Symphony No.1.
Where the symphony argues, this one breathes. Strings carry a sustained
melody while woodwinds answer. Brass enters only at the climax.
Think Barber Adagio for Strings meets Mahler slow movement.
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    crescendo,
    humanize,
    reverb,
    stereo_width,
)

song = Song(title="Cathedral", bpm=84, time_sig=(3, 4))

BAR = 3.0  # 3/4 time — 3 beats per bar
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── Violin I — the singing voice ──────────────────────────────────────────
vln1 = song.add_track(Track(name="vln1", instrument="violin", volume=0.72, pan=-0.35))
melody = humanize(
    crescendo(
        [
            Note("C", 5, 3.0),
            Note("D", 5, 1.5),
            Note("D#", 5, 1.5),
            Note("G", 5, 3.0),
            Note("F", 5, 1.5),
            Note("D#", 5, 1.5),
            Note("D", 5, 3.0),
            Note("C", 5, 6.0),
            r(3.0),
            Note("G#", 4, 3.0),
            Note("A#", 4, 1.5),
            Note("C", 5, 1.5),
            Note("D#", 5, 3.0),
            Note("D", 5, 1.5),
            Note("C", 5, 1.5),
            Note("G", 4, 3.0),
            Note("C", 4, 6.0),
        ],
        0.2,
        0.9,
    ),
    vel_spread=0.04,
    timing_spread=0.03,
)
vln1.extend(melody)

# ── Violin II — harmony a third below ────────────────────────────────────
vln2 = song.add_track(Track(name="vln2", instrument="violin", volume=0.62, pan=-0.12))
vln2.extend(
    humanize(
        crescendo(
            [
                Note("G#", 4, 3.0),
                Note("A#", 4, 1.5),
                Note("C", 5, 1.5),
                Note("D#", 5, 3.0),
                Note("C", 5, 1.5),
                Note("G#", 4, 1.5),
                Note("G", 4, 3.0),
                Note("G#", 4, 6.0),
                r(3.0),
                Note("F", 4, 3.0),
                Note("G", 4, 1.5),
                Note("G#", 4, 1.5),
                Note("C", 5, 3.0),
                Note("A#", 4, 1.5),
                Note("G#", 4, 1.5),
                Note("D#", 4, 3.0),
                Note("G#", 3, 6.0),
            ],
            0.18,
            0.82,
        ),
        vel_spread=0.04,
    )
)
vln2.extend(bars(2))

# ── Violas — inner warmth ─────────────────────────────────────────────────
vla = song.add_track(Track(name="vla", instrument="strings", volume=0.60, pan=0.12))
vla.extend(
    [
        Chord("C", "min", 3, duration=3.0, velocity=0.45),
        Chord("G", "min", 3, duration=3.0, velocity=0.42),
        Chord("D#", "maj", 3, duration=3.0, velocity=0.45),
        Chord("G", "dom7", 3, duration=3.0, velocity=0.48),
        Chord("C", "min", 3, duration=6.0, velocity=0.50),
        Chord("G#", "maj7", 3, duration=6.0, velocity=0.45),
        Chord("D#", "maj", 3, duration=3.0, velocity=0.42),
        Chord("G", "dom7", 3, duration=3.0, velocity=0.45),
        Chord("C", "min", 3, duration=6.0, velocity=0.40),
    ]
)

# ── Cello — sustained bass ────────────────────────────────────────────────
vc = song.add_track(Track(name="cello", instrument="cello", volume=0.70, pan=0.35))
vc.extend(
    crescendo(
        [
            Note("C", 3, 6.0),
            Note("G", 2, 6.0),
            Note("D#", 3, 3.0),
            Note("G", 2, 3.0),
            Note("C", 3, 6.0),
            Note("G#", 2, 6.0),
            Note("D#", 3, 3.0),
            Note("G", 2, 3.0),
            Note("C", 3, 6.0),
        ],
        0.3,
        0.8,
    )
)

# ── Oboe — answering phrase ───────────────────────────────────────────────
oboe = song.add_track(Track(name="oboe", instrument="oboe", volume=0.62, pan=0.0))
oboe.extend(bars(3))  # wait 9 bars (3/4 = 9 beats = 3 bars here)
oboe.extend(
    humanize(
        [
            Note("C", 5, 1.5),
            Note("D", 5, 0.75),
            Note("D#", 5, 0.75),
            Note("F", 5, 3.0),
            Note("D#", 5, 1.5),
            Note("C", 5, 1.5),
            Note("G", 4, 3.0),
            Note("G#", 4, 3.0),
            Note("A#", 4, 1.5),
            Note("G#", 4, 1.5),
            Note("G", 4, 3.0),
            Note("C", 5, 6.0),
        ],
        vel_spread=0.05,
    )
)

# ── French horn — enters at climax ────────────────────────────────────────
horn = song.add_track(Track(name="horn", instrument="french_horn", volume=0.72, pan=0.2))
horn.extend(bars(6))
horn.extend(
    crescendo(
        [
            Note("G", 3, 3.0),
            Note("G#", 3, 3.0),
            Note("A#", 3, 3.0),
            Note("D#", 4, 3.0),
            Note("C", 4, 6.0),
            Note("G", 3, 3.0),
            Note("D#", 3, 3.0),
            Note("C", 3, 6.0),
        ],
        0.35,
        0.88,
    )
)

song.effects = {
    "vln1": lambda s, sr: reverb(s, sr, room_size=0.85, damping=0.35, wet=0.3),
    "vln2": lambda s, sr: reverb(s, sr, room_size=0.85, damping=0.35, wet=0.3),
    "vla": lambda s, sr: reverb(s, sr, room_size=0.85, wet=0.28),
    "cello": lambda s, sr: reverb(s, sr, room_size=0.88, wet=0.3),
    "oboe": lambda s, sr: reverb(s, sr, room_size=0.75, wet=0.22),
    "horn": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.82, wet=0.28), width=1.3),
}
