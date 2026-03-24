"""upstream_two.py — Liquid DnB. 174 BPM, Am, jazzier than the first.

Where liquid_dnb.py is warm and lush, this one is more jazz-forward.
Rhodes comp with actual chord extensions, sax melody fragment,
pizzicato strings for texture, and a bass that walks properly.
Second track for the Upstream album.
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    chorus,
    compress,
    delay,
    reverb,
    stereo_width,
)

song = Song(title="Upstream II", bpm=174)

BAR = 4.0
SWING = 0.48
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── DnB kick pattern — 1 and 2.5 ─────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.95))
kick.extend(bars(4))
kick_pat = [Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5), r(1.0), Note("C", 2, 0.5), r(0.5)]
kick.extend(kick_pat * 28)
kick.extend(bars(4))

# ── Snare — beat 2 and 4 ─────────────────────────────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.78))
snare.extend(bars(4))
snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)] * 28)
snare.extend(bars(4))

# ── Swung hats ───────────────────────────────────────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.42, swing=SWING))
hat.extend(bars(4))
hat.extend([Note("F", 5, 0.5)] * (28 * 8))
hat.extend(bars(4))

# ── Reese bass — chord tones not just root ────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="reese_bass", volume=0.78))
bass.extend(bars(4))
walk = [
    Note("A", 2, 2.0),
    Note("C", 3, 1.0),
    Note("E", 3, 1.0),
    Note("F", 2, 2.0),
    Note("A", 2, 1.0),
    Note("C", 3, 1.0),
    Note("D", 2, 2.0),
    Note("F", 2, 1.0),
    Note("A", 2, 1.0),
    Note("E", 2, 2.0),
    Note("G", 2, 1.0),
    Note("B", 2, 1.0),
]
bass.extend(walk * 7)
bass.extend(bars(4))

# ── Rhodes jazz comp — extended voicings ─────────────────────────────────
comp = song.add_track(Track(name="comp", instrument="rhodes", volume=0.58, pan=-0.15, swing=SWING))
comp.extend(bars(4))
comp_loop = [
    Chord("A", "min9", 3, duration=BAR, velocity=0.6),
    Chord("F", "maj7", 3, duration=BAR, velocity=0.58),
    Chord("D", "min9", 3, duration=BAR, velocity=0.6),
    Chord("E", "dom7", 3, duration=BAR, velocity=0.62),
]
comp.extend(comp_loop * 7)
comp.extend(bars(4))

# ── Saxophone melody — jazz inflected ────────────────────────────────────
sax = song.add_track(Track(name="sax", instrument="saxophone", volume=0.68, pan=0.1, swing=SWING))
sax.extend(bars(8))
sax_phrase = [
    r(0.5),
    Note("A", 4, 0.5),
    Note("C", 5, 0.5),
    Note("E", 5, 0.5),
    Note("G", 5, 1.0),
    r(0.5),
    Note("F", 5, 0.5),
    Note("E", 5, 1.0),
    Note("D", 5, 0.5),
    r(0.5),
    r(BAR),
    Note("C", 5, 0.5),
    Note("D", 5, 0.25),
    Note("E", 5, 0.25),
    Note("G", 5, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("F", 5, 0.5),
    Note("E", 5, 2.0),
    r(1.0),
    r(BAR),
]
sax.extend(sax_phrase * 5)
sax.extend(bars(4))

# ── Pizzicato strings — texture ───────────────────────────────────────────
pizz = song.add_track(
    Track(name="pizz", instrument="pizzicato", volume=0.35, pan=-0.3, swing=SWING)
)
pizz.extend(bars(12))
pizz_pat = [
    Note("A", 4, 0.5),
    r(0.5),
    Note("E", 5, 0.5),
    r(0.5),
    Note("C", 5, 0.5),
    r(0.5),
    Note("A", 4, 0.5),
    r(0.5),
]
pizz.extend(pizz_pat * 20)
pizz.extend(bars(4))

# ── Pad — lush underneath ────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.32, pan=0.2))
pad.extend(bars(4))
for _ in range(7):
    pad.extend(comp_loop)
pad.extend(bars(4))

song._effects = {
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.75, wet=0.35), width=1.6),
    "sax": lambda s, sr: reverb(
        delay(s, sr, delay_ms=345.0, feedback=0.3, wet=0.2), sr, room_size=0.4, wet=0.12
    ),
    "comp": lambda s, sr: chorus(reverb(s, sr, room_size=0.35, wet=0.1), sr, rate_hz=0.5, wet=0.15),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.15),
}
