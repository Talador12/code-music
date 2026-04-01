"""lost_frequencies.py — Deep house / melodic techno. Cm, 122 BPM.

The middle ground between deadmau5 patience and festival EDM energy.
Deep house has a chord in it. It grooves. The bass is warm. The hat
is open on the offbeat. There's a piano melody. Everything has a slight
analog softness to it — that's the tape saturation and warm reverb.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    WHOLE,
    Note,
    Song,
    Track,
    arp,
    chord_prog,
    compress,
    conv_reverb,
    reverb,
    stereo_width,
    tape_sat,
)

song = Song(title="Lost Frequencies", bpm=122)

BAR = 4.0
r = Note.rest

PROG = chord_prog(
    ["C", "G#", "D#", "G"], ["min7", "maj7", "maj7", "dom7"], octave=3, duration=BAR, velocity=0.58
)

# ── Kick — 4-on-floor ─────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.98))
kick.extend([r(BAR)] * 4)
kick.extend([Note("C", 2, 1.0)] * (24 * 4))
kick.extend([r(BAR)] * 4)

# ── Open hat — offbeat ────────────────────────────────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.38))
hat.extend([r(BAR)] * 4)
hat.extend([r(0.5), Note("F", 5, 0.5)] * (24 * 4))
hat.extend([r(BAR)] * 4)

# ── Deep bass ─────────────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="moog_bass", volume=0.80))
bass.extend([r(BAR)] * 4)
bass_roots = [("C", 2), ("G#", 1), ("D#", 2), ("G", 2)]
for _ in range(6):
    for p, o in bass_roots:
        bass.extend(
            [Note(p, o, HALF, velocity=0.82), Note(p, o, QUARTER, velocity=0.72), r(QUARTER)]
        )
bass.extend([r(BAR)] * 4)

# ── Pad ────────────────────────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.42))
for _ in range(8):
    pad.extend(PROG)

# ── Piano melody — the emotional center ───────────────────────────────────
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.65, pan=-0.1))
piano.extend([r(BAR)] * 8)
mel = [
    Note("C", 5, QUARTER),
    r(EIGHTH),
    Note("D#", 5, EIGHTH),
    Note("G", 5, HALF),
    Note("F", 5, QUARTER),
    Note("D#", 5, QUARTER),
    r(HALF),
    r(QUARTER),
    Note("C", 5, QUARTER),
    Note("D", 5, QUARTER),
    Note("D#", 5, QUARTER),
    Note("G", 5, WHOLE),
    r(QUARTER),
    Note("G#", 4, QUARTER),
    Note("A#", 4, HALF),
    Note("G", 4, QUARTER),
    Note("F", 4, QUARTER),
    Note("D#", 4, HALF),
    Note("C", 4, WHOLE),
    r(BAR),
]
piano.extend(mel * 4)

# ── Arp — enters late, adds texture ───────────────────────────────────────
arp_tr = song.add_track(Track(name="arp", instrument="pluck", volume=0.30, pan=0.3))
arp_tr.extend([r(BAR)] * 16)
for _ in range(4):
    for ch in PROG:
        arp_tr.extend(arp(ch, pattern="up", rate=0.25, octaves=2))
arp_tr.extend([r(BAR)] * 4)

song.effects = {
    "piano": lambda s, sr: tape_sat(
        conv_reverb(s, sr, room="chamber", wet=0.3),
        sr,
        drive=1.5,
        warmth=0.5,
        wet=0.3,
    ),
    "pad": lambda s, sr: stereo_width(
        conv_reverb(s, sr, room="hall", wet=0.35),
        width=1.7,
    ),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
    "arp": lambda s, sr: reverb(s, sr, room_size=0.5, wet=0.2),
}
