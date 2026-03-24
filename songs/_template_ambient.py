"""Ambient template — 60 BPM, D Lydian, no drums, pad + piano + reverb.

Copy and rename: cp songs/_template_ambient.py songs/my_ambient_track.py
Then edit and: make play-my_ambient_track
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    conv_reverb,
    delay,
    generate_melody,
    humanize,
    stereo_width,
)

song = Song(title="My Ambient Track", bpm=60, key_sig="D")

BAR = 4.0
r = Note.rest

# ── Pad — slow chords, very wide ──────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4))
for ch, sh in [("D", "maj7"), ("A", "sus2"), ("B", "min7"), ("G", "maj7")] * 2:
    pad.add(Chord(ch, sh, 3, duration=BAR * 2, velocity=0.45))

# ── Piano — sparse notes with lots of space ───────────────────────────────
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.6))
# Generated melody — change the seed for different results
mel = generate_melody("D", scale_mode="lydian", octave=5, bars=8, density=0.3, seed=42)
piano.extend(humanize(mel, vel_spread=0.1, timing_spread=0.06))

# ── Optional: strings that enter halfway ──────────────────────────────────
strings = song.add_track(Track(name="strings", instrument="strings", volume=0.3, pan=-0.2))
strings.extend([r(BAR)] * 8)
# TODO: add string melody or chords here

song._effects = {
    "pad": lambda s, sr: stereo_width(conv_reverb(s, sr, room="hall", wet=0.45), width=1.9),
    "piano": lambda s, sr: delay(
        conv_reverb(s, sr, room="chamber", wet=0.3), sr, delay_ms=720.0, feedback=0.35, wet=0.2
    ),
}
