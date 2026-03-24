"""heavy_wobble.py — Dubstep. Half-time drums, wobble bass, the drop is a physical event.

Structure (140 BPM, Cm, half-time feel):
  Bars 1-4:   Intro — sub drone, no drums
  Bars 5-8:   Verse — half-time kit, bass groove
  Bars 9-10:  Pre-drop — strip everything, tension
  Bars 11-18: Drop 1 — full wobble, kick every beat
  Bars 19-22: Breakdown — ethereal pad, ghost melody
  Bars 23-30: Drop 2 — bigger, extra wobble layer
  Bars 31-34: Outro — decay
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    compress,
    delay,
    lowpass,
    reverb,
    stereo_width,
)

song = Song(title="Half Step", bpm=140)

BAR = 4.0
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── Sub drone — the weight underneath everything ──────────────────────────
sub = song.add_track(Track(name="sub", instrument="sub_bass", volume=0.85))
for _ in range(34):
    sub.add(Note("C", 1, BAR, velocity=0.7))

# ── Wobble bass — the whole point ─────────────────────────────────────────
wobble = song.add_track(Track(name="wobble", instrument="wobble", volume=0.88))
wobble.extend(bars(4))  # intro silence

# Verse: slow groove
verse_bass = [
    Note("C", 2, 1.0),
    Note("C", 2, 0.5),
    r(0.5),
    Note("D#", 2, 0.5),
    r(0.5),
    Note("G", 2, 0.5),
    r(0.5),
    Note("C", 2, 1.0),
    r(1.0),
    Note("C", 2, 0.5),
    r(0.5),
    Note("A#", 1, 0.5),
    Note("C", 2, 0.5),
    r(1.0),
]
wobble.extend(verse_bass * 2)  # bars 5-8

# Pre-drop: silence
wobble.extend(bars(2))

# Drop 1: hard locked 8ths
drop_bass = [Note("C", 2, 0.5, velocity=0.95)] * 16  # 2 bars
wobble.extend(drop_bass * 4)  # bars 11-18

# Breakdown: melodic bass hint
wobble.extend(
    [
        Note("C", 2, 2.0, velocity=0.4),
        Note("D#", 2, 2.0, velocity=0.4),
        Note("G", 2, 2.0, velocity=0.45),
        Note("A#", 2, 2.0, velocity=0.42),
    ]
    * 2
)  # bars 19-22

# Drop 2: harder
drop2 = [Note("C", 2, 0.25, velocity=1.0)] * 32  # 2 bars 16ths
wobble.extend(drop2 * 4)  # bars 23-30

wobble.extend(bars(4))

# ── Kick — half-time in verse, full in drop ───────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
kick.extend(bars(4))
# Verse half-time: kick on 1 and 3
kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)] * 4)
kick.extend(bars(2))  # pre-drop
# Drop: four on floor
kick.extend([Note("C", 2, 1.0)] * (8 * 4))
# Breakdown: half-time again
kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)] * 4)
# Drop 2
kick.extend([Note("C", 2, 1.0)] * (8 * 4))
kick.extend(bars(4))

# ── Snare — half-time: beat 3 only ───────────────────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.85))
snare.extend(bars(4))
snare.extend([r(2.0), Note("D", 3, 1.0), r(1.0)] * 8)  # half-time
snare.extend(bars(2))
snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)] * 8)  # drop
snare.extend([r(2.0), Note("D", 3, 1.0), r(1.0)] * 4)
snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)] * 8)
snare.extend(bars(4))

# ── Ethereal pad in breakdown ─────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=0.0))
pad.extend(bars(18))
for ch, sh in [("C", "min7"), ("D#", "maj7"), ("G", "min7"), ("A#", "maj7")] * 2:
    pad.add(Chord(ch, sh, 3, duration=BAR, velocity=0.5))
pad.extend(bars(8))

# ── Lead ghost melody in breakdown ───────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="sine", volume=0.35, pan=0.1))
lead.extend(bars(18))
lead.extend(
    [
        Note("C", 5, 1.0, velocity=0.4),
        r(1.0),
        Note("D#", 5, 2.0, velocity=0.35),
        Note("G", 5, 1.0, velocity=0.4),
        r(1.0),
        Note("F", 5, 2.0, velocity=0.35),
        Note("D#", 5, 1.0, velocity=0.38),
        r(1.0),
        Note("C", 5, 2.0, velocity=0.32),
        Note("A#", 4, 4.0, velocity=0.3),
    ]
)
lead.extend(bars(12))

song._effects = {
    "sub": lambda s, sr: lowpass(s, sr, cutoff_hz=100.0),
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.8, wet=0.45), width=1.9),
    "lead": lambda s, sr: delay(s, sr, delay_ms=429.0, feedback=0.4, wet=0.3),
    "wobble": lambda s, sr: compress(s, sr, threshold=0.55, ratio=4.0, makeup_gain=1.15),
}
