"""psy_gate.py — Psytrance. Am, 145 BPM. Goa-style acid lead and rolling bass.

A driving psytrance track with the classic 16th-note bass pattern, acid-tinged
lead, and gated pad layers. Infected Mushroom / Astrix adjacent.

Style: Psytrance, Am, 145 BPM.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    delay,
    gate,
    lfo_filter,
    reverb,
    stereo_width,
)

song = Song(title="Psy Gate", bpm=145)

r = Note.rest

# ── Kick — four on the floor, punchy ─────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.85))
for _ in range(32):
    kick.extend([Note("C", 2, 1.0)] * 4)

# ── Bass — rolling 16th note psytrance bass ──────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.65, pan=0.0))
bass_bar = [
    Note("A", 2, 0.25),
    Note("A", 2, 0.25),
    Note("A", 2, 0.25),
    Note("A", 2, 0.25),
    Note("A", 2, 0.25),
    Note("C", 3, 0.25),
    Note("A", 2, 0.25),
    Note("A", 2, 0.25),
    Note("A", 2, 0.25),
    Note("A", 2, 0.25),
    Note("G", 2, 0.25),
    Note("A", 2, 0.25),
    Note("A", 2, 0.25),
    Note("A", 2, 0.25),
    Note("E", 2, 0.25),
    Note("A", 2, 0.25),
]
for _ in range(32):
    bass.extend(bass_bar)

# ── Lead — acid-style melody ─────────────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=0.15))
lead_phrase = [
    r(16.0),  # sit out first 4 bars
    Note("E", 5, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("D", 5, 0.5),
    Note("E", 5, 0.5),
    Note("A", 5, 1.0),
    Note("G", 5, 0.5),
    Note("E", 5, 0.5),
    Note("D", 5, 1.0),
    r(3.0),
    Note("C", 5, 0.5),
    Note("D", 5, 0.5),
    Note("E", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A", 5, 1.0),
    Note("E", 5, 1.0),
    Note("D", 5, 2.0),
    r(6.0),
]
for _ in range(4):
    lead.extend(lead_phrase)

# ── Pad — gated atmosphere ───────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=0.0))
for _ in range(16):
    pad.extend(
        [
            Chord("A", "min", 3, duration=4.0),
            Chord("F", "maj", 3, duration=4.0),
        ]
    )

song.effects = {
    "bass": EffectsChain().add(lfo_filter, rate=0.5, depth=0.5),
    "lead": EffectsChain()
    .add(delay, delay_ms=207, feedback=0.3, wet=0.2)
    .add(reverb, room_size=0.4, wet=0.15),
    "pad": EffectsChain()
    .add(gate, rate_hz=4.0, shape="trapezoid")
    .add(reverb, room_size=0.7, wet=0.35)
    .add(stereo_width, width=1.6),
}
