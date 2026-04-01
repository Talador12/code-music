"""on_the_one.py — Funk. Moog bass, Rhodes stabs, clap on 2&4. 108 BPM, Em.

James Brown said 'on the one' — hit beat 1 hard, lock everything to it.
Sly Stone, Parliament-Funkadelic, Prince. The groove is the argument.
Everything else decorates the pocket. Chicken-scratch guitar implied.
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

song = Song(title="On the One", bpm=108)

BAR = 4.0
r = Note.rest

# ── Kick — on the one, hard ───────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.98))
kick_pat = [Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5), r(1.0), Note("C", 2, 0.5), r(0.5)]
for _ in range(16):
    kick.extend(kick_pat)

# ── Clap — 2 & 4, tight ──────────────────────────────────────────────────
clap = song.add_track(Track(name="clap", instrument="drums_clap", volume=0.85, swing=0.5))
for _ in range(16):
    clap.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])

# ── Hi-hat — 16th notes, swung ────────────────────────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.38, swing=0.5))
for _ in range(16):
    hat.extend([Note("F", 5, EIGHTH)] * 8)

# ── Moog bass — the whole argument ───────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="moog_bass", volume=0.92, swing=0.5))
groove = [
    Note("E", 2, EIGHTH),
    Note("E", 2, EIGHTH),
    r(EIGHTH),
    Note("G", 2, EIGHTH),
    Note("E", 2, EIGHTH),
    r(EIGHTH),
    Note("A", 2, EIGHTH),
    Note("E", 2, EIGHTH),
    Note("G", 2, QUARTER),
    r(EIGHTH),
    Note("E", 2, EIGHTH),
    Note("E", 2, QUARTER),
    Note("D", 2, EIGHTH),
    Note("E", 2, EIGHTH),
]
for _ in range(16):
    bass.extend(groove)

# ── Rhodes stabs — syncopated, percussive ─────────────────────────────────
comp = song.add_track(Track(name="comp", instrument="rhodes", volume=0.68, swing=0.5, pan=-0.15))
stabs = [
    Chord("E", "min7", 3, duration=EIGHTH, velocity=0.82),
    r(EIGHTH),
    r(QUARTER),
    Chord("E", "min7", 3, duration=EIGHTH, velocity=0.78),
    r(EIGHTH),
    Chord("A", "dom7", 3, duration=EIGHTH, velocity=0.75),
    r(EIGHTH),
    r(HALF),
]
for _ in range(16):
    comp.extend(stabs)

# ── Lead melody — enters at bar 5, pentatonic Em ─────────────────────────
lead = song.add_track(Track(name="lead", instrument="wurlitzer", volume=0.62, swing=0.5, pan=0.2))
lead.extend([r(BAR)] * 4)
mel = [
    r(EIGHTH),
    Note("G", 5, EIGHTH),
    Note("A", 5, QUARTER),
    Note("B", 5, EIGHTH),
    Note("A", 5, EIGHTH),
    Note("G", 5, QUARTER),
    r(EIGHTH),
    Note("E", 5, EIGHTH),
    Note("G", 5, EIGHTH),
    Note("E", 5, EIGHTH),
    Note("D", 5, HALF),
    r(EIGHTH),
    Note("E", 5, EIGHTH),
    Note("G", 5, EIGHTH),
    Note("A", 5, EIGHTH),
    Note("B", 5, QUARTER),
    Note("A", 5, EIGHTH),
    Note("G", 5, EIGHTH),
    Note("E", 5, HALF),
    r(QUARTER),
    Note("G", 5, QUARTER),
]
for _ in range(12):
    lead.extend(mel)

song.effects = {
    "bass": lambda s, sr: compress(s, sr, threshold=0.45, ratio=5.0, makeup_gain=1.2),
    "comp": lambda s, sr: chorus(reverb(s, sr, room_size=0.3, wet=0.1), sr, rate_hz=0.6, wet=0.12),
}
