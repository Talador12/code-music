"""cinematic_rise.py — Hans Zimmer inspired hybrid orchestral trailer music.

Style: Inception/Interstellar era. Massive low-end drones, taiko percussion,
choir swells, rising string ostinatos, epic brass moments.

Signature elements:
  - Taiko drums for impact hits (new preset)
  - Sub bass drone throughout
  - String ostinato (short repeated motif — the Zimmer fingerprint)
  - Choir aah building through the middle
  - Brass unison at the peak
  - Reverse swell into the main hit
  - Lots of space and silence — less is more

Structure (100 BPM):
  Bars 1-4:   Silence → first drone hit
  Bars 5-8:   String ostinato begins over Cm drone
  Bars 9-12:  Choir enters, rising
  Bars 13-16: Full brass hit — the money moment
  Bars 17-20: Pull back — only strings + choir
  Bars 21-24: Second peak — everything, bigger
  Bars 25-28: Final fade — solo cello over sub drone
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    crescendo,
    decrescendo,
    lowpass,
    reverb,
    stereo_width,
)

song = Song(title="Weight", bpm=100)

BAR = 4.0
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── Sub bass drone — C throughout ────────────────────────────────────────
sub = song.add_track(Track(name="sub", instrument="sub_bass", volume=0.7, pan=0.0))
# Slow swell
sub.extend(bars(4))  # silence
for _ in range(24):
    sub.add(Note("C", 1, BAR, velocity=0.6))

# ── Taiko hits — sporadic, massive impact ────────────────────────────────
taiko = song.add_track(Track(name="taiko", instrument="taiko", volume=1.0))
taiko.extend(bars(4))
# Ostinato phase: kick on 1 and 3
for _ in range(4):
    taiko.extend(
        [Note("C", 2, 1.0, velocity=0.9), r(1.0), Note("C", 2, 1.0, velocity=0.75), r(1.0)]
    )
# Choir phase: accent hits
taiko.extend(
    [
        r(BAR),
        Note("C", 2, 0.5, velocity=1.0),
        r(3.5),
        Note("G", 2, 0.5, velocity=0.9),
        r(3.5),
        r(BAR),
        Note("C", 2, 0.5, velocity=1.0),
        r(3.5),
    ]
)
# Brass hit: huge hits
taiko.extend(
    [Note("C", 2, 1.0, velocity=1.0)] * 2
    + [r(1.0)]
    + [Note("C", 2, 0.5, velocity=1.0)]
    + [r(0.5)]
    + [Note("C", 2, 2.0, velocity=1.0)]
    + [r(2.0)]
)
# Pull back: sparse
taiko.extend(bars(2) + [Note("C", 2, 0.5, velocity=0.7), r(3.5)] + bars(1))
# Second peak
for _ in range(2):
    taiko.extend(
        [Note("C", 2, 0.5, velocity=1.0)] * 4 + [Note("C", 2, 2.0, velocity=0.95)] + [r(2.0)]
    )
# Outro
taiko.extend(bars(4))

# ── String ostinato — short repeating figure in Cm ──────────────────────
ostinato_motif = [
    Note("C", 4, 0.5),
    Note("D#", 4, 0.5),
    Note("G", 4, 0.5),
    Note("A#", 4, 0.5),
]
vln1 = song.add_track(Track(name="vln1", instrument="violin", volume=0.65, pan=-0.3))
vln1.extend(bars(4))
for i in range(24):
    vel = 0.4 + min(0.5, i * 0.025)
    vln1.extend([Note(n.pitch, duration=0.5, velocity=vel) for n in ostinato_motif])

# ── String counterline ────────────────────────────────────────────────────
vln2 = song.add_track(Track(name="vln2", instrument="strings", volume=0.55, pan=0.3))
vln2.extend(bars(8))  # enters bar 9
counter = crescendo(
    [
        Note("G", 4, 1.0),
        Note("F", 4, 1.0),
        Note("D#", 4, 1.0),
        Note("C", 4, 1.0),
    ]
    * 4
    + [
        Note("G", 4, 2.0),
        Note("A#", 4, 2.0),
        Note("C", 5, 4.0),
        Note("A#", 4, 2.0),
        Note("G", 4, 2.0),
        Note("F", 4, 2.0),
        Note("D#", 4, 2.0),
        Note("C", 4, 4.0),
    ],
    0.2,
    0.9,
)
vln2.extend(counter)
vln2.extend(bars(4))

# ── Cello sustained lines ─────────────────────────────────────────────────
vc = song.add_track(Track(name="cello", instrument="cello", volume=0.7, pan=0.15))
vc.extend(bars(4))
vc_line = crescendo(
    [
        Note("C", 3, 4.0),
        Note("G", 2, 4.0),
        Note("D#", 3, 4.0),
        Note("A#", 2, 4.0),
        Note("F", 2, 4.0),
        Note("G", 2, 4.0),
        Note("C", 3, 8.0),
        Note("D#", 3, 4.0),
        Note("G", 3, 4.0),
        Note("C", 3, 4.0),
        Note("A#", 2, 4.0),
        Note("C", 3, 8.0),
    ],
    0.3,
    0.9,
)
vc.extend(vc_line)
vc.extend(bars(4))

# ── Choir — enters bar 9, swells ─────────────────────────────────────────
choir = song.add_track(Track(name="choir", instrument="choir_aah", volume=0.55, pan=0.0))
choir.extend(bars(8))
choir_swell = crescendo(
    [
        Chord("C", "min", 3, duration=4.0),
        Chord("G", "min", 3, duration=4.0),
        Chord("D#", "maj", 3, duration=4.0),
        Chord("A#", "maj", 3, duration=4.0),
        Chord("C", "min", 3, duration=4.0),
        Chord("G", "min", 3, duration=4.0),
        Chord("D#", "maj", 3, duration=8.0),
    ],
    0.2,
    0.9,
)
choir.extend(choir_swell)
choir.extend(bars(4))

# ── Brass unison hit — bars 13-16 and 21-24 ──────────────────────────────
for inst, pan_v, vol in [
    ("trumpet", -0.3, 0.85),
    ("trombone", 0.3, 0.8),
    ("french_horn", 0.0, 0.75),
]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=vol, pan=pan_v))
    tr.extend(bars(12))  # silent until bar 13
    # First hit (bars 13-16)
    brass_hit_1 = crescendo(
        [
            Note("C", 4 if inst == "trumpet" else 3, 0.5, velocity=0.6),
            Note("D#", 4 if inst == "trumpet" else 3, 0.5, velocity=0.75),
            Note("G", 4 if inst == "trumpet" else 3, 2.0, velocity=0.95),
            r(1.0),
            Note("C", 4 if inst == "trumpet" else 3, 1.0, velocity=0.9),
            Note("D#", 4 if inst == "trumpet" else 3, 0.5, velocity=0.85),
            Note("G", 4 if inst == "trumpet" else 3, 3.5, velocity=0.95),
        ],
        0.5,
        1.0,
    )
    tr.extend(brass_hit_1)
    tr.extend(bars(4))  # bars 17-20: rest
    # Second hit (bars 21-24): bigger
    brass_hit_2 = crescendo(
        [
            Note("G", 4 if inst == "trumpet" else 3, 1.0, velocity=1.0),
            Note("C", 5 if inst == "trumpet" else 4, 1.0, velocity=1.0),
            Note("D#", 5 if inst == "trumpet" else 4, 2.0, velocity=1.0),
            Note("C", 5 if inst == "trumpet" else 4, 0.5, velocity=0.9),
            Note("G", 4 if inst == "trumpet" else 3, 0.5, velocity=0.85),
            Note("D#", 4 if inst == "trumpet" else 3, 0.5, velocity=0.8),
            Note("C", 4 if inst == "trumpet" else 3, 2.5, velocity=0.95),
        ],
        0.8,
        1.0,
    )
    tr.extend(brass_hit_2)
    tr.extend(bars(4))  # outro

# ── Outro solo cello ──────────────────────────────────────────────────────
solo_vc = song.add_track(Track(name="solo_vc", instrument="cello", volume=0.7, pan=-0.1))
solo_vc.extend(bars(24))
solo_vc.extend(
    decrescendo(
        [
            Note("C", 3, 2.0),
            Note("G", 2, 2.0),
            Note("D#", 3, 2.0),
            r(2.0),
            Note("C", 3, 4.0),
            Note("G", 2, 4.0),
            Note("C", 3, 8.0),
        ],
        0.7,
        0.05,
    )
)

# ── Effects ───────────────────────────────────────────────────────────────
song.effects = {
    "sub": EffectsChain().add(lowpass, cutoff_hz=100.0, q=0.5),
    "vln1": EffectsChain().add(reverb, room_size=0.8, damping=0.4, wet=0.3),
    "vln2": EffectsChain().add(reverb, room_size=0.85, wet=0.35),
    "cello": EffectsChain().add(reverb, room_size=0.85, wet=0.3),
    "solo_vc": EffectsChain().add(reverb, room_size=0.9, wet=0.4),
    "choir": EffectsChain()
    .add(reverb, room_size=0.9, damping=0.5, wet=0.45)
    .add(stereo_width, width=1.8),
    "trumpet": EffectsChain().add(reverb, room_size=0.8, wet=0.25),
    "trombone": EffectsChain().add(reverb, room_size=0.8, wet=0.25),
    "french_horn": EffectsChain().add(reverb, room_size=0.85, wet=0.3),
}
