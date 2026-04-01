"""liquid_dnb.py — Liquid Drum & Bass, 174 BPM, D minor.

Style: LTJ Bukem, Goldie, Hospital Records era liquid DnB.
Warm, melodic, jazzy. No distorted drops — it floats.

Signature elements:
  - Fast breakbeat-style drums (not amen — liquid DnB uses cleaner breaks)
  - Reese bass holding long chord tones
  - Rhodes / piano over jazz-inflected chords
  - Lush reverbed pads
  - Atmospheric flute or string melody
  - Subtle snare rolls every 2 bars

Structure (174 BPM, 4/4):
  Bars 1-4:   Intro — pads + atmospheric melody
  Bars 5-12:  Verse — drums in, Reese bass, piano comp
  Bars 13-20: Bridge — melodic peak, strings rise
  Bars 21-28: Drop — full texture, bass pushes
  Bars 29-32: Outro — strip back, fade to pads
"""

from code_music import (
    Note,
    Song,
    Track,
    chord_prog,
    chorus,
    compress,
    delay,
    reverb,
    scale,
    stereo_width,
)

song = Song(title="Upstream", bpm=174)

BAR = 4.0
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── Chord loop: Dm9 - Bb - F - Am (warm minor) ───────────────────────────
ROOTS = ["D", "A#", "F", "A"]
SHAPES = ["min9", "maj7", "maj7", "min7"]
PROG = chord_prog(ROOTS, SHAPES, octave=3, duration=BAR, velocity=0.55)

# ── Kick — syncopated DnB pattern ────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.95))
# Classic DnB: kick on 1 and the 'and' of 2 (beats 1 and 2.5)
kick_pat = [
    Note("C", 2, 1.0),
    r(0.5),
    Note("C", 2, 0.5),
    r(1.0),
    Note("C", 2, 0.5),
    r(0.5),
]  # 4 beats = 1 bar
kick.extend(bars(4))
kick.extend(kick_pat * 28)
kick.extend(bars(4))

# ── Snare — backbeat with rolls ───────────────────────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.8))
snare.extend(bars(4))
s = Note("D", 3, 1.0)
snare_pat = [r(1.0), s, r(1.0), s]  # 2 & 4
roll = [Note("D", 3, 0.25)] * 4  # snare roll
for i in range(28):
    if i % 8 == 7:  # every 2 bars, add a roll on beat 4
        snare.extend([r(1.0), s, r(1.0)] + roll)
    else:
        snare.extend(snare_pat)
snare.extend(bars(4))

# ── Hi-hat — 8th notes with occasional 16th bursts ───────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.4))
hat.extend(bars(4))
h_8th = [Note("F", 5, 0.5)] * 8
h_16th = [Note("F", 5, 0.25)] * 4
for i in range(28):
    if i % 4 == 3:
        hat.extend(h_8th[:4] + h_16th)
    else:
        hat.extend(h_8th)
hat.extend(bars(4))

# ── Reese bass — long sustained tones per chord ───────────────────────────
bass = song.add_track(Track(name="bass", instrument="reese_bass", volume=0.75, pan=0.0))
bass.extend(bars(4))
bass_roots = [("D", 2), ("A#", 1), ("F", 2), ("A", 2)]
# Verse: root + occasional chromatic passing tone
for _ in range(2):
    for p, o in bass_roots:
        bass.extend(
            [
                Note(p, o, 2.0, velocity=0.8),
                Note(p, o, 0.5, velocity=0.7),
                r(0.5),
                Note(p, o, 1.0, velocity=0.75),
            ]
        )
# Bridge: busier bass movement
for _ in range(2):
    for p, o, pp, po in [("D", 2, "F", 2), ("A#", 1, "C", 2), ("F", 2, "G", 2), ("A", 2, "C", 3)]:
        bass.extend(
            [
                Note(p, o, 1.0, velocity=0.85),
                Note(pp, po, 0.5, velocity=0.7),
                Note(p, o, 0.5, velocity=0.8),
                Note(p, o, 2.0, velocity=0.75),
            ]
        )
# Drop: punchy bass
for _ in range(2):
    for p, o in bass_roots:
        bass.extend([Note(p, o, 0.5, velocity=0.9)] * 4 + [Note(p, o, 2.0, velocity=0.85)])
bass.extend(bars(4))

# ── Rhodes comp ──────────────────────────────────────────────────────────
rhodes = song.add_track(
    Track(name="rhodes", instrument="rhodes", volume=0.6, pan=-0.15, swing=0.45)
)
rhodes.extend(bars(4))
for _ in range(7):
    rhodes.extend(PROG)
rhodes.extend(bars(4))

# ── Atmospheric pad ───────────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=0.1))
for _ in range(8):
    pad.extend(PROG)
pad.extend(bars(4))

# ── Atmospheric melody — scale-based flute line ──────────────────────────
mel = song.add_track(Track(name="mel", instrument="flute", volume=0.55, pan=0.2))
d_notes = scale("D", "dorian", octave=5, length=7)
phrase = [
    d_notes[0],
    Note.rest(0.5),
    d_notes[2],
    d_notes[3],
    d_notes[4],
    Note.rest(0.5),
    d_notes[5],
    d_notes[6],
]
# Set durations
for i, n in enumerate(phrase):
    if n.pitch is not None:
        phrase[i] = Note(n.pitch, duration=0.5, velocity=0.55 + i * 0.02)
mel.extend(bars(0))
# Bars 1-4: atmospheric solo line
mel.extend(phrase * 2)
# Bars 5-12: simpler comp
mel.extend(
    [Note(n.pitch, duration=1.0, velocity=0.5) if n.pitch else Note.rest(1.0) for n in d_notes[:4]]
    * 4
)
# Bars 13-20: full melodic peak
mel.extend(phrase * 4)
# Bars 21-28: drop melody
mel.extend(phrase * 4)
# Bars 29-32: fade out
mel.extend(
    [
        Note(d_notes[0].pitch, duration=2.0, velocity=0.3),
        Note.rest(2.0),
        Note(d_notes[2].pitch, duration=4.0, velocity=0.2),
    ]
)
mel.add(Note.rest(8.0))

# ── Effects ───────────────────────────────────────────────────────────────
song.effects = {
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.75, wet=0.35), width=1.6),
    "mel": lambda s, sr: reverb(
        delay(s, sr, delay_ms=345.0, feedback=0.35, wet=0.25), sr, room_size=0.5, wet=0.2
    ),
    "rhodes": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.4, wet=0.12), sr, rate_hz=0.6, wet=0.2
    ),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.15),
}
