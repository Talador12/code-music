"""gospel_hour.py — Gospel / soul choir. 76 BPM, Bb major. Full SATB + organ + piano.

Church music at its best is the most powerful communal experience in music.
Everyone singing together, the same words, in a room that amplifies it.
This is that feeling: choir call-and-response, Hammond organ underneath,
upright piano driving the harmony, building to a full congregation moment.
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    chorus,
    crescendo,
    reverb,
    stereo_width,
)

song = Song(title="Gospel Hour", bpm=76)

BAR = 4.0
SWING = 0.48
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── Organ — the foundation, never stops ───────────────────────────────────
organ = song.add_track(Track(name="organ", instrument="organ", volume=0.52))
prog = [
    Chord("A#", "maj7", 3, duration=BAR * 2, velocity=0.6),
    Chord("F", "maj7", 3, duration=BAR * 2, velocity=0.58),
    Chord("G", "min7", 3, duration=BAR * 2, velocity=0.6),
    Chord("C", "dom7", 3, duration=BAR * 2, velocity=0.62),
]
organ.extend(prog * 4)

# ── Piano — call and response rhythm ─────────────────────────────────────
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.65, swing=SWING))
piano_comp = [
    Chord("A#", "maj", 3, duration=1.0, velocity=0.75),
    r(1.0),
    Chord("A#", "maj", 3, duration=0.5, velocity=0.7),
    r(1.5),
    Chord("F", "maj", 3, duration=1.0, velocity=0.72),
    r(1.0),
    Chord("F", "maj", 3, duration=0.5, velocity=0.68),
    r(1.5),
    Chord("G", "min", 3, duration=1.0, velocity=0.73),
    r(1.5),
    Chord("G", "min", 3, duration=0.5, velocity=0.68),
    r(1.0),
    Chord("C", "dom7", 3, duration=1.0, velocity=0.75),
    r(1.0),
    Chord("C", "dom7", 3, duration=0.5, velocity=0.72),
    r(1.5),
]
piano.extend(piano_comp * 4)

# ── Bass — walking gospel ─────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="contrabass", volume=0.72, swing=SWING))
bass_walk = [
    Note("A#", 2, 1.0),
    Note("C", 3, 1.0),
    Note("D", 3, 1.0),
    Note("F", 3, 1.0),
    Note("F", 2, 1.0),
    Note("G", 2, 1.0),
    Note("A", 2, 1.0),
    Note("C", 3, 1.0),
    Note("G", 2, 1.0),
    Note("A#", 2, 1.0),
    Note("C", 3, 1.0),
    Note("D", 3, 1.0),
    Note("C", 2, 1.0),
    Note("D", 2, 1.0),
    Note("E", 2, 1.0),
    Note("G", 2, 1.0),
]
bass.extend(bass_walk * 4)

# ── Choir — SATB layers ───────────────────────────────────────────────────
# Soprano
sop = song.add_track(Track(name="soprano", instrument="choir_ooh", volume=0.62, pan=-0.1))
sop.extend(bars(4))  # enters after intro
sop_mel = crescendo(
    [
        Note("A#", 5, 2.0),
        Note("C", 6, 1.0),
        Note("D", 6, 1.0),
        Note("F", 6, 3.0),
        r(1.0),
        Note("D", 6, 1.0),
        Note("C", 6, 1.0),
        Note("A#", 5, 2.0),
        Note("A#", 5, 4.0),
        Note("G", 5, 2.0),
        Note("A#", 5, 1.0),
        Note("C", 6, 1.0),
        Note("D", 6, 2.0),
        Note("C", 6, 1.0),
        Note("A#", 5, 1.0),
        Note("A#", 5, 4.0),
    ],
    0.4,
    0.95,
)
sop.extend(sop_mel * 3)

# Alto
alt = song.add_track(Track(name="alto", instrument="choir_aah", volume=0.58, pan=0.1))
alt.extend(bars(4))
alt.extend(
    crescendo(
        [
            Note("F", 5, 2.0),
            Note("G", 5, 1.0),
            Note("A#", 5, 1.0),
            Note("C", 6, 3.0),
            r(1.0),
            Note("A#", 5, 1.0),
            Note("G", 5, 1.0),
            Note("F", 5, 2.0),
            Note("F", 5, 4.0),
            Note("D#", 5, 2.0),
            Note("F", 5, 1.0),
            Note("G", 5, 1.0),
            Note("A#", 5, 2.0),
            Note("G", 5, 1.0),
            Note("F", 5, 1.0),
            Note("F", 5, 4.0),
        ],
        0.35,
        0.88,
    )
    * 3
)

# Bass voice
bv = song.add_track(Track(name="bass_voice", instrument="choir_aah", volume=0.60, pan=0.0))
bv.extend(bars(8))  # bass voice enters late
bv.extend(
    crescendo(
        [
            Note("A#", 3, 4.0),
            Note("F", 3, 4.0),
            Note("G", 3, 4.0),
            Note("C", 4, 4.0),
            Note("A#", 3, 4.0),
            Note("F", 3, 4.0),
            Note("G", 3, 4.0),
            Note("C", 4, 4.0),
        ],
        0.3,
        0.88,
    )
    * 3
)

# ── Drums — gospel kit ────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.85))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.78, swing=SWING))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35, swing=SWING))
ride = song.add_track(Track(name="ride", instrument="drums_ride", volume=0.42, swing=SWING))

for _ in range(16):
    kick.extend([Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5), r(1.0), Note("C", 2, 1.0)])
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])
    hat.extend([Note("F", 5, 0.5)] * 8)
    ride.extend(
        [Note("F", 5, 0.5), Note("F", 5, 0.25), Note("F", 5, 0.25)] * 3
        + [Note("F", 5, 0.5), r(0.5)]
    )

song._effects = {
    "soprano": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.92, wet=0.5), width=1.7),
    "alto": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.92, wet=0.48), width=1.5),
    "bass_voice": lambda s, sr: reverb(s, sr, room_size=0.88, wet=0.42),
    "organ": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.75, wet=0.3), sr, rate_hz=0.3, wet=0.12
    ),
}
