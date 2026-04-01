"""chiptune_quest.py — Chiptune / 8-bit. Square waves, arpeggiated chords, NES energy.

Structure: 160 BPM, D major, video game boss fight energy.
  Bars 1-4:   Title screen — simple melody
  Bars 5-8:   World map — arpeggiated chords
  Bars 9-16:  Level theme — full texture
  Bars 17-20: Boss intro — tension
  Bars 21-28: Boss theme — intense, fast arps
  Bars 29-32: Victory fanfare — resolution
"""

from code_music import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    WHOLE,
    Note,
    Song,
    Track,
    crescendo,
    reverb,
)

song = Song(title="Save Point", bpm=160)

BAR = 4.0
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── Lead melody — pulse wave (square) ────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="square", volume=0.7))

# Title screen: simple 8-bit melody in D major
title = [
    Note("D", 5, QUARTER),
    Note("F#", 5, QUARTER),
    Note("A", 5, QUARTER),
    Note("D", 6, QUARTER),
    Note("A", 5, EIGHTH),
    Note("F#", 5, EIGHTH),
    Note("D", 5, HALF),
    Note("E", 5, QUARTER),
    Note("G", 5, QUARTER),
    Note("B", 5, QUARTER),
    Note("E", 6, QUARTER),
    Note("B", 5, EIGHTH),
    Note("G", 5, EIGHTH),
    Note("E", 5, HALF),
]
lead.extend(title)

# World map: wandering
world = [
    Note("D", 5, EIGHTH),
    Note("E", 5, EIGHTH),
    Note("F#", 5, EIGHTH),
    Note("G", 5, EIGHTH),
    Note("A", 5, QUARTER),
    Note("F#", 5, EIGHTH),
    Note("D", 5, EIGHTH),
    Note("B", 4, EIGHTH),
    Note("C#", 5, EIGHTH),
    Note("D", 5, EIGHTH),
    Note("E", 5, EIGHTH),
    Note("A", 4, HALF),
    Note("G", 5, EIGHTH),
    Note("F#", 5, EIGHTH),
    Note("E", 5, QUARTER),
    Note("D", 5, EIGHTH),
    Note("C#", 5, EIGHTH),
    Note("D", 5, HALF),
]
lead.extend(world)

# Level theme
level_melody = [
    Note("D", 5, EIGHTH),
    Note("F#", 5, EIGHTH),
    Note("A", 5, EIGHTH),
    Note("D", 6, EIGHTH),
    Note("C#", 6, EIGHTH),
    Note("A", 5, EIGHTH),
    Note("F#", 5, QUARTER),
    Note("G", 5, EIGHTH),
    Note("B", 5, EIGHTH),
    Note("D", 6, EIGHTH),
    Note("G", 6, EIGHTH),
    Note("F#", 6, EIGHTH),
    Note("D", 6, EIGHTH),
    Note("B", 5, QUARTER),
    Note("A", 5, EIGHTH),
    Note("G", 5, EIGHTH),
    Note("F#", 5, EIGHTH),
    Note("E", 5, EIGHTH),
    Note("D", 5, EIGHTH),
    Note("C#", 5, EIGHTH),
    Note("D", 5, HALF),
    Note("A", 5, DOTTED_QUARTER),
    Note("G", 5, EIGHTH),
    Note("F#", 5, QUARTER),
    Note("E", 5, QUARTER),
    Note("D", 5, HALF),
    r(HALF),
]
lead.extend(level_melody * 2)

# Boss intro: low, threatening
boss_intro = [
    Note("D", 4, EIGHTH),
    r(EIGHTH),
    Note("D", 4, EIGHTH),
    r(EIGHTH),
    Note("D#", 4, QUARTER),
    Note("D", 4, QUARTER),
    r(HALF),
    Note("C#", 4, EIGHTH),
    r(EIGHTH),
    Note("C#", 4, EIGHTH),
    r(EIGHTH),
    Note("D", 4, HALF),
    r(HALF),
]
lead.extend(boss_intro)

# Boss theme: faster, more intense
boss = [
    Note("D", 5, EIGHTH),
    Note("C#", 5, EIGHTH),
    Note("D", 5, EIGHTH),
    Note("D#", 5, EIGHTH),
    Note("D", 5, EIGHTH),
    Note("C#", 5, EIGHTH),
    Note("B", 4, QUARTER),
    Note("A", 4, EIGHTH),
    Note("A#", 4, EIGHTH),
    Note("A", 4, EIGHTH),
    Note("G#", 4, EIGHTH),
    Note("A", 4, HALF),
    Note("F", 4, EIGHTH),
    Note("F#", 4, EIGHTH),
    Note("G", 4, EIGHTH),
    Note("G#", 4, EIGHTH),
    Note("A", 4, EIGHTH),
    Note("A#", 4, EIGHTH),
    Note("B", 4, QUARTER),
    Note("D", 5, HALF),
    r(HALF),
]
lead.extend(boss * 2)

# Victory fanfare
fanfare = crescendo(
    [
        Note("D", 5, EIGHTH),
        Note("D", 5, EIGHTH),
        Note("D", 5, EIGHTH),
        Note("D", 5, QUARTER),
        Note("A#", 4, EIGHTH),
        Note("C", 5, EIGHTH),
        Note("D", 5, HALF),
        Note("F#", 5, EIGHTH),
        Note("F#", 5, EIGHTH),
        Note("F#", 5, EIGHTH),
        Note("F#", 5, QUARTER),
        Note("D", 5, EIGHTH),
        Note("E", 5, EIGHTH),
        Note("F#", 5, WHOLE),
    ],
    start_vel=0.6,
    end_vel=1.0,
)
lead.extend(fanfare)

# ── Harmony square — a third above ───────────────────────────────────────
harm = song.add_track(Track(name="harm", instrument="square", volume=0.5, pan=-0.25))
harm.extend(bars(8))  # no harmony in title/world
harm_level = [
    Note("F#", 5, EIGHTH),
    Note("A", 5, EIGHTH),
    Note("C#", 6, EIGHTH),
    Note("F#", 6, EIGHTH),
    Note("E", 6, EIGHTH),
    Note("C#", 6, EIGHTH),
    Note("A", 5, QUARTER),
    Note("B", 5, EIGHTH),
    Note("D", 6, EIGHTH),
    Note("F#", 6, EIGHTH),
    Note("B", 6, EIGHTH),
    Note("A", 6, EIGHTH),
    Note("F#", 6, EIGHTH),
    Note("D", 6, QUARTER),
    Note("C#", 6, EIGHTH),
    Note("B", 5, EIGHTH),
    Note("A", 5, EIGHTH),
    Note("G", 5, EIGHTH),
    Note("F#", 5, EIGHTH),
    Note("E", 5, EIGHTH),
    Note("F#", 5, HALF),
    Note("C#", 6, DOTTED_QUARTER),
    Note("B", 5, EIGHTH),
    Note("A", 5, QUARTER),
    Note("G", 5, QUARTER),
    Note("F#", 5, HALF),
    r(HALF),
]
harm.extend(harm_level * 2)
harm.extend(bars(12))

# ── Triangle bass — sub melody ───────────────────────────────────────────
tri_bass = song.add_track(Track(name="tri_bass", instrument="triangle", volume=0.65, pan=0.2))

bass_line = [
    Note("D", 4, QUARTER),
    r(QUARTER),
    Note("D", 4, QUARTER),
    r(QUARTER),
    Note("A", 3, QUARTER),
    r(QUARTER),
    Note("A", 3, QUARTER),
    r(QUARTER),
    Note("G", 3, QUARTER),
    r(QUARTER),
    Note("G", 3, QUARTER),
    r(QUARTER),
    Note("A", 3, HALF),
    r(HALF),
]
tri_bass.extend(bars(8))
tri_bass.extend(bass_line * 6)

# ── NES drums — noise channel ─────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.85))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.7))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.4))

kick.extend(bars(4))
snare.extend(bars(4))
hat.extend(bars(4))

for _ in range(28):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])
    hat.extend([Note("F", 5, 0.5)] * 8)

# 16th hat in boss section — just the last 8 bars
hat.extend(bars(12))
for _ in range(8):
    hat.extend([Note("F", 5, 0.25)] * 16)
hat.extend(bars(4))
kick.extend(bars(4))
snare.extend(bars(4))

song.effects = {
    "lead": lambda s, sr: reverb(s, sr, room_size=0.25, wet=0.08),
    "harm": lambda s, sr: reverb(s, sr, room_size=0.25, wet=0.08),
}
