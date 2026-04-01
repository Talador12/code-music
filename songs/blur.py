"""blur.py — Shoegaze. D major, 92 BPM. Everything is reverb.

Shoegaze is the genre where you can't tell where the guitar ends and
the reverb begins. My Bloody Valentine, Slowdive, Cocteau Twins.
Multiple layers of distorted guitar through massive reverb and chorus.
The vocals (if present) are another texture, not a lead voice.
The melody is felt more than heard. Everything blurs together.
"""

from code_music import (
    EIGHTH,
    Chord,
    Note,
    Song,
    Track,
    arp,
    chorus,
    conv_reverb,
    distortion,
    humanize,
    reverb,
    stereo_width,
)

song = Song(title="Blur", bpm=92, key_sig="D")

BAR = 4.0
r = Note.rest

# ── Guitar wall 1 — distorted, massive reverb, left ───────────────────────
gtr1 = song.add_track(Track(name="gtr1", instrument="guitar_electric", volume=0.55, pan=-0.4))
chords_1 = [
    Chord("D", "maj7", 3, duration=BAR * 2, velocity=0.65),
    Chord("A", "sus2", 3, duration=BAR * 2, velocity=0.62),
    Chord("B", "min7", 3, duration=BAR * 2, velocity=0.65),
    Chord("G", "maj7", 3, duration=BAR * 2, velocity=0.62),
]
gtr1.extend(chords_1 * 2)

# ── Guitar wall 2 — different voicing, right ──────────────────────────────
gtr2 = song.add_track(Track(name="gtr2", instrument="guitar_electric", volume=0.50, pan=0.4))
chords_2 = [
    Chord("D", "add9", 4, duration=BAR * 2, velocity=0.58),
    Chord("A", "maj7", 4, duration=BAR * 2, velocity=0.55),
    Chord("B", "min", 4, duration=BAR * 2, velocity=0.58),
    Chord("G", "add9", 4, duration=BAR * 2, velocity=0.55),
]
gtr2.extend(chords_2 * 2)

# ── Guitar 3 — arpeggiated, center, emerges halfway ───────────────────────
gtr3 = song.add_track(Track(name="gtr3", instrument="guitar_ks", volume=0.42, pan=0.0))
gtr3.extend([r(BAR)] * 8)
for ch in [("D", "maj7"), ("A", "sus2"), ("B", "min7"), ("G", "maj7")]:
    gtr3.extend(
        humanize(
            arp(Chord(ch[0], ch[1], 4), pattern="up_down", rate=EIGHTH, octaves=2),
            vel_spread=0.1,
            timing_spread=0.03,
        )
    )

# ── Bass — deep, sustained, simple ────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.68))
bass.extend(
    [
        Note("D", 2, BAR * 2),
        Note("A", 1, BAR * 2),
        Note("B", 1, BAR * 2),
        Note("G", 1, BAR * 2),
    ]
    * 2
)

# ── Drums — minimal, buried in the mix ────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.72))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.55))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.22))

for _ in range(16):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 0.5), r(0.5), r(1.0)])
    snare.extend(
        [r(1.0), Note("D", 3, 1.0, velocity=0.5), r(1.0), Note("D", 3, 1.0, velocity=0.45)]
    )
    hat.extend([Note("F", 5, EIGHTH, velocity=0.22)] * 8)

# ── Pad — sine, barely there, very wide ────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.25))
for ch in [("D", "maj7"), ("A", "sus2"), ("B", "min7"), ("G", "maj7")] * 2:
    pad.add(Chord(ch[0], ch[1], 2, duration=BAR * 2, velocity=0.35))

song.effects = {
    "gtr1": lambda s, sr: stereo_width(
        distortion(conv_reverb(s, sr, room="hall", wet=0.6), drive=2.5, tone=0.4, wet=0.7),
        width=1.8,
    ),
    "gtr2": lambda s, sr: stereo_width(
        chorus(
            distortion(conv_reverb(s, sr, room="hall", wet=0.55), drive=2.2, tone=0.45, wet=0.65),
            sr,
            rate_hz=0.4,
            wet=0.3,
        ),
        width=1.7,
    ),
    "gtr3": lambda s, sr: conv_reverb(s, sr, room="chamber", wet=0.45),
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.95, wet=0.6), width=1.9),
    "snare": lambda s, sr: conv_reverb(s, sr, room="hall", wet=0.5),
}
