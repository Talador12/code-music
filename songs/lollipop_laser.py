"""lollipop_laser.py — Mord Fustang-inspired cosmic electro/disco-house.

Style cues:
- That iconic Mord Fustang neon-laser lead: fast sawtooth arp with heavy
  chorusing, playing major/minor 7th arpeggios in strict 16th-note grid
- Disco-house 4-on-floor kick with offbeat open hats and a clap on 2 & 4
- Lush chord pads in Eb major (bright, cosmic, almost euphoric)
- Punchy Motown-ish bass: locked to kick, octave jumps
- Pluck/lead melody that floats above the arp with wide vibrato feel
- Retro breakdown: strip to arp + pad, then full re-entry with swell

Structure (bars, 4/4 at 128 BPM):
  1-4   Intro: pads + arp only
  5-8   Verse: add bass + kit
  9-12  Bridge: melody enters, kit fills
  13-16 Chorus drop: everything + laser lead full blast
  17-18 Mini-breakdown: arp + pad only (2 bars)
  19-22 Second chorus: full texture
  23-26 Outro: reduce, pads swell out
"""

from code_music import Chord, Note, Song, Track, chorus, delay, reverb

song = Song(title="Lollipop Laser", bpm=128)

BAR = 4.0
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── Key: Eb major ─────────────────────────────────────────────────────────────
# Chord loop: Ebmaj7 - Cm7 - Abmaj7 - Bb (two bars each in intro)
EBMAJ7 = Chord("D#", "maj7", 3, duration=BAR, velocity=0.6)
CM7 = Chord("C", "min7", 3, duration=BAR, velocity=0.6)
ABMAJ7 = Chord("G#", "maj7", 3, duration=BAR, velocity=0.6)
BB7 = Chord("A#", "dom7", 3, duration=BAR, velocity=0.6)
LOOP = [EBMAJ7, CM7, ABMAJ7, BB7]

# ── Pad — whole track, slow attack, wide stereo ───────────────────────────────
pad_l = song.add_track(Track(name="pad_l", instrument="pad", volume=0.38, pan=-0.5))
pad_r = song.add_track(Track(name="pad_r", instrument="pad", volume=0.38, pan=0.5))
for pad in (pad_l, pad_r):
    pad.extend(LOOP * 6 + [EBMAJ7, CM7])  # 26 bars

# ── Laser arp — 16th-note sawtooth arpeggio, the signature sound ──────────────
arp = song.add_track(Track(name="arp", instrument="sawtooth", volume=0.55, pan=0.0))


def arp_pat(notes_16th):
    """Build one bar of 16th-note arpeggio from a list of midi/name pitches."""
    return [Note(p, o, 0.25, velocity=0.75) for p, o in notes_16th]


eb_arp = arp_pat([("D#", 4), ("G", 4), ("A#", 4), ("D#", 5)] * 4)  # Ebmaj arpeggio
cm_arp = arp_pat([("C", 4), ("D#", 4), ("G", 4), ("C", 5)] * 4)
ab_arp = arp_pat([("G#", 3), ("C", 4), ("D#", 4), ("G#", 4)] * 4)
bb_arp = arp_pat([("A#", 3), ("D", 4), ("F", 4), ("A#", 4)] * 4)
arp_loop = eb_arp + cm_arp + ab_arp + bb_arp  # 4 bars

arp.extend(arp_loop * 6 + eb_arp + cm_arp)  # 26 bars

# ── Kick — 4-on-floor, starts bar 5 ──────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
k = Note("C", 2, 1.0)
kick.extend(bars(4))
kick.extend([k, k, k, k] * 18)  # bars 5-22
kick.extend(bars(4))

# ── Clap — 2 & 4, starts bar 5 ───────────────────────────────────────────────
clap = song.add_track(Track(name="clap", instrument="drums_snare", volume=0.75))
cl = Note("D", 3, 1.0)
clap.extend(bars(4))
clap.extend([r(1.0), cl, r(1.0), cl] * 18)
clap.extend(bars(4))

# ── Open hi-hat — offbeats (2.5 of each beat) → every 0.5 offset from kick ──
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.5))
h = Note("F", 5, 0.5)
hat.extend(bars(4))
hat.extend([r(0.5), h] * (8 * 18))  # 8 offbeat 8ths per bar × 18 bars
hat.extend(bars(4))

# ── Disco bass — locked to kick with octave jumps ─────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.8, pan=0.0))
bass.extend(bars(4))


# Per chord-bar bass pattern: root quarter, up-octave 8th, root 8th, root quarter, rest quarter
def bass_bar(p, o):
    return [
        Note(p, o, 1.0, velocity=0.85),
        Note(p, o + 1, 0.5, velocity=0.7),
        Note(p, o, 0.5, velocity=0.75),
        Note(p, o, 1.0, velocity=0.8),
        r(1.0),
    ]


bass_roots = [("D#", 2), ("C", 2), ("G#", 1), ("A#", 1)]
for _ in range(4):
    for p, o in bass_roots:
        bass.extend(bass_bar(p, o))
# mini-breakdown bars 17-18: just root whole note
for p, o in [("D#", 2), ("C", 2)]:
    bass.add(Note(p, o, BAR, velocity=0.5))
# second chorus 19-22
for p, o in bass_roots:
    bass.extend(bass_bar(p, o))
# outro bars 23-26: fade to root quarter only
for p, o in bass_roots:
    bass.add(Note(p, o, 1.0, velocity=0.4))
    bass.extend(bars(1)[:-1] + [r(BAR - 1.0)])  # rest of bar

# ── Melody lead — pluck synth, enters bar 9 ───────────────────────────────────
melody = song.add_track(Track(name="melody", instrument="pluck", volume=0.65, pan=0.1))
melody.extend(bars(8))

# Bridge melody (bars 9-12): stepwise, major-key optimism
bridge_mel = [
    Note("D#", 5, 0.5),
    Note("F", 5, 0.5),
    Note("G", 5, 1.0),
    Note("G", 5, 0.5),
    Note("F", 5, 0.5),
    Note("D#", 5, 1.0),
    Note("C", 5, 0.5),
    Note("D#", 5, 0.5),
    Note("F", 5, 1.0),
    Note("G", 5, 2.0),
    r(2.0),
    Note("G#", 4, 0.5),
    Note("A#", 4, 0.5),
    Note("C", 5, 1.0),
    Note("D#", 5, 1.0),
    Note("C", 5, 1.0),
    Note("A#", 4, 1.0),
    r(1.0),
    Note("A#", 4, 0.5),
    Note("C", 5, 0.5),
    Note("D#", 5, 0.5),
    Note("F", 5, 0.5),
    Note("G", 5, 2.0),
    r(2.0),
]
melody.extend(bridge_mel)

# Chorus melody (bars 13-16): peak anthem, higher octave
chorus_mel = [
    Note("D#", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A#", 5, 1.0),
    Note("A#", 5, 0.5),
    Note("G", 5, 0.5),
    Note("F", 5, 1.0),
    Note("D#", 5, 0.5),
    Note("F", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A#", 5, 0.5),
    Note("A#", 5, 2.0),
    r(2.0),
    Note("C", 6, 0.5),
    Note("A#", 5, 0.5),
    Note("G", 5, 1.0),
    Note("F", 5, 0.5),
    Note("D#", 5, 0.5),
    Note("C", 5, 1.0),
    r(1.0),
    Note("D#", 5, 0.5),
    Note("F", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A#", 5, 0.5),
    Note("D#", 6, 2.0),
    r(2.0),
]
melody.extend(chorus_mel)

# Mini-breakdown bars 17-18: ghost high note
melody.extend([Note("D#", 5, 2.0, velocity=0.25), r(BAR)])

# Second chorus (bars 19-22)
melody.extend(chorus_mel)

# Outro bars 23-26: melody fades with long notes
melody.extend(
    [
        Note("D#", 5, 2.0, velocity=0.5),
        Note("G", 4, 2.0, velocity=0.35),
        Note("G#", 4, 2.0, velocity=0.3),
        Note("A#", 4, 2.0, velocity=0.25),
        Note("D#", 4, 4.0, velocity=0.2),
        r(BAR),
    ]
)

# ── Effects hints (applied by render pipeline) ────────────────────────────────
song.effects = {
    "pad_l": lambda s, sr: reverb(s, sr, room_size=0.75, damping=0.5, wet=0.35),
    "pad_r": lambda s, sr: reverb(s, sr, room_size=0.75, damping=0.5, wet=0.35),
    "arp": lambda s, sr: chorus(
        delay(s, sr, delay_ms=187.5, feedback=0.25, wet=0.2, ping_pong=True),
        sr,
        rate_hz=1.2,
        depth_ms=2.5,
        wet=0.45,
    ),
    "melody": lambda s, sr: reverb(
        delay(s, sr, delay_ms=375.0, feedback=0.35, wet=0.3),
        sr,
        room_size=0.6,
        wet=0.2,
    ),
}
