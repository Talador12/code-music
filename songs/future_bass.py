"""future_bass.py — future bass / melodic dubstep, 150 BPM, F# major.

Style: Illenium / Marshmello / Flume. Big supersaw chords, heavy sidechain,
emotional lead melody, choppy vocal chops, half-time drum feel in verse,
full 4-on-floor in chorus drop.

Structure:
  Bars 1-4:   Intro — pad chords + soft piano melody
  Bars 5-8:   Verse — half-time drums, bass enters, supersaw pads
  Bars 9-12:  Pre-chorus — builds with snare rolls + filter sweep
  Bars 13-20: Chorus drop — full supersaw wall, sidechain pump, anthem
  Bars 21-24: Bridge — strip to piano + voice pad + arpeggios
  Bars 25-32: Second drop — even bigger, extra octave lead
  Bars 33-36: Outro — pads decay
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    arp,
    delay,
    reverb,
    stereo_width,
)

song = Song(title="Between", bpm=150)

BAR = 4.0
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# F# major chords: F#maj7 - D#m7 - Bmaj7 - C#dom7
LOOP = [
    Chord("F#", "maj7", 3, duration=BAR),
    Chord("D#", "min7", 3, duration=BAR),
    Chord("B", "maj7", 3, duration=BAR),
    Chord("C#", "dom7", 3, duration=BAR),
]

# ── Kick ──────────────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
kick.extend(bars(4))  # intro: no kick
# Verse: half-time kick (every 2 bars)
kick.extend([Note("C", 2, 1.0), r(1.0), r(BAR), Note("C", 2, 1.0), r(1.0), r(BAR)] * 2)
# Pre-chorus: 4-on-floor
kick.extend([Note("C", 2, 1.0)] * 16)
# Chorus: 4-on-floor
kick.extend([Note("C", 2, 1.0)] * 32)
# Bridge: half-time
kick.extend([Note("C", 2, 1.0), r(1.0), r(BAR), Note("C", 2, 1.0), r(1.0), r(BAR)] * 2)
# 2nd drop: 4-on-floor
kick.extend([Note("C", 2, 1.0)] * 32)
kick.extend(bars(4))

# ── Clap / Snare ──────────────────────────────────────────────────────────
clap = song.add_track(Track(name="clap", instrument="drums_clap", volume=0.8))
clap.extend(bars(4))
# Verse: half-time snare (bar 3 and 7 of each section)
clap.extend([r(BAR), r(BAR), r(1.0), Note("D", 3, 1.0), r(1.0), r(BAR - 1.0)] * 2)
# Pre-chorus: snare on 2+4
clap.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)] * 4)
# Chorus: 2+4
clap.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)] * 8)
clap.extend(bars(4))
clap.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)] * 8)
clap.extend(bars(4))

# ── Hi-hat ────────────────────────────────────────────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35))
hat.extend(bars(4))
hat.extend([Note("F", 5, 0.5)] * (28 * 8))
hat.extend(bars(4))

# ── 808 bass ──────────────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="drums_808", volume=0.9))
bass.extend(bars(4))
roots_beat = {  # per-chord 808 pattern
    "F#": [Note("F#", 1, 0.5), Note("F#", 1, 0.5), r(1.0), Note("F#", 1, 0.5), r(1.5)],
    "D#": [Note("D#", 1, 0.5), Note("D#", 1, 0.5), r(1.0), Note("D#", 1, 0.5), r(1.5)],
    "B": [Note("B", 1, 0.5), Note("B", 1, 0.5), r(1.0), Note("B", 1, 0.5), r(1.5)],
    "C#": [Note("C#", 1, 0.5), Note("C#", 1, 0.5), r(1.0), Note("C#", 2, 0.5), r(1.5)],
}
for _ in range(8):  # bars 5-36
    for root, pat in roots_beat.items():
        bass.extend(pat)
bass.extend(bars(4))

# ── Supersaw pad ──────────────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="supersaw", volume=0.5, pan=0.0))
# Intro: soft pad
for ch in LOOP:
    pad.add(Chord(ch.root, ch.shape, ch.octave, duration=BAR, velocity=0.45))
# Verse through outro
for _ in range(8):
    pad.extend(LOOP)

# ── Piano intro melody ────────────────────────────────────────────────────
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.7, pan=-0.15))
intro_mel = [
    Note("F#", 4, 0.5),
    Note("G#", 4, 0.5),
    Note("A#", 4, 1.0),
    Note("C#", 5, 0.5),
    Note("A#", 4, 0.5),
    Note("G#", 4, 1.0),
    Note("F#", 4, 0.5),
    Note("G#", 4, 0.25),
    Note("A#", 4, 0.25),
    Note("C#", 5, 1.0),
    Note("F#", 4, 1.0),
    r(1.0),
    Note("D#", 4, 0.5),
    Note("F#", 4, 0.5),
    Note("G#", 4, 1.0),
    Note("A#", 4, 0.5),
    Note("G#", 4, 0.5),
    Note("F#", 4, 2.0),
]
piano.extend(intro_mel)  # intro bars 1-4
piano.extend(bars(8))  # verse + pre-chorus: rest
piano.extend(bars(8))  # chorus: rest
# Bridge (bars 21-24): piano returns
piano.extend(intro_mel)
piano.extend(bars(12))  # 2nd drop + outro: rest

# ── Anthem lead melody (supersaw) — chorus only ───────────────────────────
lead = song.add_track(Track(name="lead", instrument="supersaw", volume=0.6, pan=0.1))
lead.extend(bars(12))  # silent until chorus

chorus_mel = [
    Note("F#", 5, 0.5),
    Note("G#", 5, 0.5),
    Note("A#", 5, 1.0),
    Note("C#", 6, 0.5),
    Note("A#", 5, 0.5),
    Note("G#", 5, 1.0),
    Note("F#", 5, 0.5),
    Note("G#", 5, 0.5),
    Note("A#", 5, 0.5),
    Note("C#", 6, 0.5),
    Note("F#", 6, 2.0),
    Note("D#", 5, 0.5),
    Note("F#", 5, 0.5),
    Note("G#", 5, 1.0),
    Note("A#", 5, 0.5),
    Note("G#", 5, 0.5),
    Note("F#", 5, 1.0),
    Note("G#", 5, 0.5),
    Note("A#", 5, 0.5),
    Note("C#", 6, 1.0),
    Note("F#", 5, 2.0),
]
lead.extend(chorus_mel * 2)  # 8 bars
lead.extend(bars(4))  # bridge: rest
lead.extend(chorus_mel * 2)  # 2nd drop (8 bars)
lead.extend(bars(4))

# ── 16th-note arp ─────────────────────────────────────────────────────────
arp_tr = song.add_track(Track(name="arp", instrument="pluck", volume=0.35, pan=-0.3))
arp_tr.extend(bars(4))
for _ in range(32):  # bars 5-36
    for ch in LOOP:
        arp_tr.extend(arp(ch, pattern="up", rate=0.25, octaves=2))
arp_tr.extend(bars(4))

# ── Choir pad ─────────────────────────────────────────────────────────────
vox_pad = song.add_track(Track(name="vox_pad", instrument="choir_ooh", volume=0.4, pan=0.25))
vox_pad.extend(bars(12))  # enters at chorus
for _ in range(4):
    vox_pad.extend(LOOP)
vox_pad.extend(bars(4))
for _ in range(2):
    vox_pad.extend(LOOP)
vox_pad.extend(bars(4))

# ── Effects ───────────────────────────────────────────────────────────────
song.effects = {
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.55, wet=0.2), width=1.7),
    "lead": lambda s, sr: delay(s, sr, delay_ms=200.0, feedback=0.25, wet=0.18, ping_pong=True),
    "vox_pad": lambda s, sr: reverb(s, sr, room_size=0.8, wet=0.4),
    "arp": lambda s, sr: reverb(s, sr, room_size=0.4, wet=0.15),
    "piano": lambda s, sr: reverb(s, sr, room_size=0.5, wet=0.2),
}
