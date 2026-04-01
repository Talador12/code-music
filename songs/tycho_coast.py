"""tycho_coast.py — Downtempo / chillout. F major, 98 BPM.

Bonobo, Tycho, Emancipator territory. Warm, textured, organic electronic.
Not lo-fi (which is deliberately degraded) — this is polished, layered,
and expensive-sounding. Guitars over electronic drums, wide pads, tape warmth.
"""

from code_music import (
    EIGHTH,
    HALF,
    Chord,
    Note,
    Song,
    Track,
    arp,
    conv_reverb,
    humanize,
    reverb,
    stereo_width,
    tape_sat,
)

song = Song(title="Tycho Coast", bpm=98, key_sig="F")
BAR = 4.0
r = Note.rest

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.38))
for ch, sh in [("F", "maj7"), ("C", "sus2"), ("D", "min7"), ("A#", "maj7")] * 3:
    pad.add(Chord(ch, sh, 3, duration=BAR * 2, velocity=0.45))

gtr = song.add_track(Track(name="guitar", instrument="guitar_ks", volume=0.62, pan=-0.2))
for ch, sh in [("F", "maj7"), ("C", "sus2"), ("D", "min7"), ("A#", "maj7")] * 3:
    gtr.extend(
        humanize(
            arp(Chord(ch, sh, 4), pattern="up_down", rate=EIGHTH, octaves=2),
            vel_spread=0.09,
            timing_spread=0.03,
        )
    )

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.82))
kick.extend([r(BAR)] * 4)
kick.extend([Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5), r(2.0)] * 20)

snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.58))
snare.extend([r(BAR)] * 4)
snare.extend(
    [r(1.0), Note("D", 3, 1.0, velocity=0.5), r(1.0), Note("D", 3, 1.0, velocity=0.45)] * 20
)

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.28))
hat.extend([r(BAR)] * 4)
hat.extend([Note("F", 5, EIGHTH, velocity=0.25)] * (20 * 8))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.68))
bass.extend([r(BAR)] * 4)
bass.extend([Note("F", 2, HALF), Note("C", 2, HALF), Note("D", 2, HALF), Note("A#", 1, HALF)] * 10)

song.effects = {
    "pad": lambda s, sr: stereo_width(conv_reverb(s, sr, room="hall", wet=0.4), width=1.8),
    "guitar": lambda s, sr: tape_sat(
        conv_reverb(s, sr, room="chamber", wet=0.25), sr, drive=1.3, warmth=0.5, wet=0.3
    ),
    "bass": lambda s, sr: reverb(s, sr, room_size=0.35, wet=0.1),
}
