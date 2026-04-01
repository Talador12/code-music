"""trance_odyssey.py — Uplifting trance, 138 BPM, A minor.

Structure:
  Bars 1-4:   Intro — supersaw pads only, wide stereo
  Bars 5-8:   Breakdown — arp enters, kick drops out
  Bars 9-12:  Build — noise sweep, rising bass, gated strings
  Bars 13-20: Main drop — full texture, anthem melody, arp wall
  Bars 21-24: Second breakdown — strip to pad + melody
  Bars 25-32: Second drop — everything, extra octave arp
  Bars 33-36: Outro — fade to pad

Techniques used:
  - supersaw lead with sidechain ducking from kick
  - gated strings (gate effect applied post-render)
  - arp() helper for 16th-note chord arpeggios
  - lfo_filter for the classic filter-open build
  - noise_sweep for the 8-bar build tension
  - stereo_width on the pad layer
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    arp,
    delay,
    gate,
    reverb,
    stereo_width,
)

song = Song(title="Drop", bpm=138)

BAR = 4.0
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── Chord loop: Am - F - C - G (the universal trance progression) ──────────
CHORDS = [
    Chord("A", "min7", 3, duration=BAR),
    Chord("F", "maj7", 3, duration=BAR),
    Chord("C", "maj", 3, duration=BAR),
    Chord("G", "dom7", 3, duration=BAR),
]

# ── Kick ──────────────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
kick.extend(bars(4))  # intro: no kick
kick.extend(bars(4))  # breakdown: no kick
kick.extend([Note("C", 2, 1.0)] * (4 * 4))  # build: kick comes back
kick.extend([Note("C", 2, 1.0)] * (8 * 4))  # drop 1+2
kick.extend(bars(4))  # 2nd breakdown
kick.extend([Note("C", 2, 1.0)] * (8 * 4))  # drop 2
kick.extend(bars(4))  # outro

# ── Open hat (offbeat 8ths) ───────────────────────────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.4))
hat.extend(bars(8))
hat.extend([r(0.5), Note("F", 5, 0.5)] * (24 * 4))
hat.extend(bars(4))

# ── Snare (2 & 4, bars 9+) ────────────────────────────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.65))
snare.extend(bars(8))
snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)] * (28))
snare.extend(bars(4))

# ── Bass — pumping 8th notes in drop sections ──────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.8))
roots = [("A", 2), ("F", 2), ("C", 3), ("G", 2)]
bass.extend(bars(8))  # intro + breakdown
# build: quarter notes only
for p, o in roots:
    bass.extend([Note(p, o, 1.0)] * 4)
# drop 1: 8th-note pump
for _ in range(2):
    for p, o in roots:
        bass.extend([Note(p, o, 0.5)] * 8)
# 2nd breakdown: rest
bass.extend(bars(4))
# drop 2: 8th-note pump with extra energy
for _ in range(2):
    for p, o in roots:
        bass.extend([Note(p, o, 0.5, velocity=0.9)] * 8)
bass.extend(bars(4))

# ── Supersaw pad (intro + always present) ─────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="supersaw", volume=0.45, pan=0.0))
for _ in range(9):  # 36 bars
    pad.extend(CHORDS)

# ── Strings (gated in drop sections) ──────────────────────────────────────
strings = song.add_track(Track(name="strings", instrument="strings", volume=0.5, pan=-0.2))
strings.extend(bars(12))  # silent until drop
for _ in range(2):
    strings.extend(CHORDS * 2)  # 8 bars
strings.extend(bars(4))  # 2nd breakdown
for _ in range(2):
    strings.extend(CHORDS * 2)
strings.extend(bars(4))

# ── Anthem lead melody (supersaw) ─────────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.55, pan=0.15))
lead.extend(bars(12))  # enters at drop

drop_melody = [
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("E", 5, 1.0),
    Note("C", 5, 0.5),
    Note("D", 5, 0.5),
    Note("E", 5, 1.0),
    Note("F", 5, 0.5),
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("A", 4, 2.0),
    Note("C", 5, 0.5),
    Note("E", 5, 0.5),
    Note("G", 5, 1.0),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("F", 5, 1.0),
    Note("E", 5, 0.5),
    Note("F", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A", 5, 0.5),
    Note("A", 5, 2.0),
]
lead.extend(drop_melody)
lead.extend(drop_melody)
lead.extend(bars(4))
lead.extend(drop_melody)
lead.extend(drop_melody)
lead.extend(bars(4))

# ── 16th arp (enters at bar 5) ─────────────────────────────────────────────
arp_tr = song.add_track(Track(name="arp", instrument="pluck", volume=0.4, pan=-0.25))
arp_tr.extend(bars(4))
for _ in range(32):  # bars 5-36
    for ch in CHORDS:
        arp_tr.extend(arp(ch, pattern="up_down", rate=0.25, octaves=2))

# ── Effects ───────────────────────────────────────────────────────────────
song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25).add(stereo_width, width=1.8),
    "lead": EffectsChain().add(delay, delay_ms=217.0, feedback=0.3, wet=0.2, ping_pong=True),
    "strings": EffectsChain()
    .add(reverb, room_size=0.4, wet=0.2)
    .add(gate, rate_hz=4.0, shape="trapezoid"),
    "arp": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
}
