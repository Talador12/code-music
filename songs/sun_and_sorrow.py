"""sun_and_sorrow.py — Reggae / roots. Gm, 80 BPM. Off-beat skank, bass & riddim.

The skank (off-beat guitar chop) is the defining rhythm of reggae —
everything hits on the 2-and and 4-and, which is the opposite of rock.
Walking bass that feels like it floats. Organ fills. Rim shot on 3.
Inspired by: Culture, Burning Spear, Steel Pulse, The Abyssinians.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    Chord,
    Note,
    Song,
    Track,
    chorus,
    compress,
    reverb,
)

song = Song(title="Sun and Sorrow", bpm=80)

BAR = 4.0
r = Note.rest

# ── Reggae skank guitar — off-beat, staccato chords ──────────────────────
skank = song.add_track(Track(name="skank", instrument="guitar_acoustic", volume=0.68, pan=-0.2))
# Classic skank: silence on beats 1,2,3,4 — chop on the "ands"
skank_bar = [
    r(EIGHTH),
    Chord("G", "min7", 3, duration=EIGHTH, velocity=0.82),
    r(EIGHTH),
    Chord("G", "min7", 3, duration=EIGHTH, velocity=0.78),
    r(EIGHTH),
    Chord("D#", "maj7", 3, duration=EIGHTH, velocity=0.80),
    r(EIGHTH),
    Chord("D#", "maj7", 3, duration=EIGHTH, velocity=0.75),
]
skank.extend(skank_bar * 16)

# ── Bass — melodic, walking, reggae feel ──────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.85))
bass_line = [
    Note("G", 2, QUARTER),
    Note("G", 2, EIGHTH),
    Note("A#", 2, EIGHTH),
    Note("D", 3, QUARTER),
    Note("C", 3, QUARTER),
    Note("D#", 2, QUARTER),
    Note("D#", 2, EIGHTH),
    Note("F", 2, EIGHTH),
    Note("G", 2, QUARTER),
    Note("A#", 2, QUARTER),
]
bass.extend(bass_line * 8)

# ── Kick — on 1 and 3, softened ──────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.72))
for _ in range(16):
    kick.extend(
        [Note("C", 2, 1.0, velocity=0.65), r(1.0), Note("C", 2, 1.0, velocity=0.60), r(1.0)]
    )

# ── Rim shot on 3 — the reggae backbeat marker ────────────────────────────
rim = song.add_track(Track(name="rim", instrument="drums_snare", volume=0.58))
for _ in range(16):
    rim.extend([r(2.0), Note("D", 3, 1.0, velocity=0.55), r(1.0)])

# ── Hi-hat — 8th notes, light ─────────────────────────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.32))
for _ in range(16):
    hat.extend([Note("F", 5, EIGHTH, velocity=0.30)] * 8)

# ── Organ fills — Hammond stabs between phrases ───────────────────────────
organ = song.add_track(Track(name="organ", instrument="organ", volume=0.45, pan=0.25))
organ_fill = [
    r(2.0),
    Chord("G", "min7", 3, duration=QUARTER, velocity=0.6),
    r(QUARTER),
    r(BAR),
    r(2.0),
    Chord("D#", "maj7", 3, duration=QUARTER, velocity=0.58),
    Chord("G", "min7", 3, duration=QUARTER, velocity=0.6),
]
organ.extend(organ_fill * 8)

# ── Melody — flute, laid back ─────────────────────────────────────────────
mel = song.add_track(Track(name="melody", instrument="flute", volume=0.52, pan=0.1))
mel.extend([r(BAR)] * 4)
phrase = [
    Note("G", 5, QUARTER),
    r(EIGHTH),
    Note("F", 5, EIGHTH),
    Note("D#", 5, HALF),
    Note("D", 5, QUARTER),
    r(QUARTER),
    Note("C", 5, HALF),
    r(QUARTER),
    Note("A#", 4, QUARTER),
    Note("C", 5, QUARTER),
    r(QUARTER),
    Note("D", 5, HALF),
    r(HALF),
]
mel.extend(phrase * 3)

song._effects = {
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.15),
    "organ": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.4, wet=0.15), sr, rate_hz=0.4, wet=0.15
    ),
    "melody": lambda s, sr: reverb(s, sr, room_size=0.55, wet=0.2),
}
