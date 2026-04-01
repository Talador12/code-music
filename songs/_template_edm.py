"""EDM template — 128 BPM, Am, four-on-the-floor, supersaw pad, sidechain bass.

Copy and rename: cp songs/_template_edm.py songs/my_edm_track.py
Then edit and: make play-my_edm_track
"""

from code_music import (
    Note,
    Song,
    Track,
    chord_prog,
    compress,
    delay,
    reverb,
    stereo_width,
)

song = Song(title="My EDM Track", bpm=128)

BAR = 4.0
r = Note.rest

# ── Change these chords to taste ──────────────────────────────────────────
PROG = chord_prog(
    ["A", "F", "C", "G"], ["min7", "maj7", "maj", "dom7"], octave=3, duration=BAR, velocity=0.6
)

# ── Kick — four on the floor ──────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
kick.extend([Note("C", 2, 1.0)] * 32)

# ── Snare — 2 & 4 ─────────────────────────────────────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.78))
snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)] * 8)

# ── Hi-hat — offbeat 8ths ─────────────────────────────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.42))
hat.extend([r(0.5), Note("F", 5, 0.5)] * 32)

# ── Supersaw pad ──────────────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="supersaw", volume=0.5))
pad.extend(PROG * 2)

# ── Bass — 8th-note pump ──────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.75))
for ch in PROG * 2:
    bass.extend([Note(ch.root, ch.octave - 1, 0.5, velocity=0.8)] * 8)

# ── Lead melody — write yours here ────────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.6))
lead.extend([r(BAR)] * 4)
# TODO: add your melody here
lead.extend([r(BAR)] * 4)

song.effects = {
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.5, wet=0.2), width=1.7),
    "lead": lambda s, sr: delay(s, sr, delay_ms=234.0, feedback=0.3, wet=0.2, ping_pong=True),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
}
