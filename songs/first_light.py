"""first_light.py — Ambient / post-rock. D major, 68 BPM. Song #60.

The 60th song. Guitar KS arpeggios over a pad that barely moves.
Strings enter halfway through. No drums. The kind of music that
plays when something in a film is about to change but hasn't yet.
Explosions in the Sky meets Brian Eno.
"""

from code_music import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    WHOLE,
    Chord,
    Note,
    Song,
    Track,
    arp,
    conv_reverb,
    crescendo,
    decrescendo,
    delay,
    humanize,
    stereo_width,
)

song = Song(title="First Light", bpm=68, key_sig="D")

BAR = 4.0
r = Note.rest

# ── Pad — barely there, very wide ──────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.32, pan=0.0))
for ch, sh in [("D", "maj7"), ("A", "sus2"), ("B", "min7"), ("G", "maj7")] * 4:
    pad.add(Chord(ch, sh, 3, duration=BAR * 2, velocity=0.4))

# ── Guitar KS — fingerpicked arpeggios ────────────────────────────────────
gtr = song.add_track(Track(name="guitar", instrument="guitar_ks", volume=0.72, pan=-0.15))

d_arp = humanize(
    arp(Chord("D", "maj7", 3), pattern="up_down", rate=EIGHTH, octaves=2),
    vel_spread=0.10,
    timing_spread=0.03,
)
a_arp = humanize(
    arp(Chord("A", "sus2", 3), pattern="up_down", rate=EIGHTH, octaves=2),
    vel_spread=0.10,
    timing_spread=0.03,
)
b_arp = humanize(
    arp(Chord("B", "min7", 3), pattern="up_down", rate=EIGHTH, octaves=2),
    vel_spread=0.10,
    timing_spread=0.03,
)
g_arp = humanize(
    arp(Chord("G", "maj7", 3), pattern="up_down", rate=EIGHTH, octaves=2),
    vel_spread=0.10,
    timing_spread=0.03,
)

for _ in range(2):
    gtr.extend(d_arp)
    gtr.extend(a_arp)
    gtr.extend(b_arp)
    gtr.extend(g_arp)

# Melody emerges from the arps
melody = humanize(
    crescendo(
        [
            Note("D", 5, DOTTED_QUARTER),
            Note("E", 5, EIGHTH),
            Note("F#", 5, HALF),
            Note("A", 5, QUARTER),
            Note("G", 5, QUARTER),
            r(HALF),
            Note("F#", 5, DOTTED_QUARTER),
            Note("E", 5, EIGHTH),
            Note("D", 5, HALF),
            Note("B", 4, WHOLE),
            r(HALF),
            Note("A", 4, QUARTER),
            Note("B", 4, QUARTER),
            Note("D", 5, HALF),
            Note("E", 5, HALF),
            Note("F#", 5, WHOLE),
            r(BAR),
        ],
        0.4,
        0.85,
    ),
    vel_spread=0.07,
    timing_spread=0.04,
)
gtr.extend(melody)

# Outro arps — decrescendo
gtr.extend(decrescendo(d_arp + a_arp, 0.65, 0.15))

# ── Strings — enter at the halfway point ──────────────────────────────────
for inst, pan_v, vol in [("violin", -0.3, 0.45), ("strings", 0.2, 0.42), ("cello", 0.35, 0.48)]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=vol, pan=pan_v))
    tr.extend([r(BAR)] * 8)  # silent first half
    tr.extend(
        crescendo(
            [
                Chord("D", "maj7", 3 if inst != "cello" else 2, duration=BAR * 2, velocity=0.3),
                Chord("A", "sus2", 3 if inst != "cello" else 2, duration=BAR * 2, velocity=0.32),
                Chord("B", "min7", 3 if inst != "cello" else 2, duration=BAR * 2, velocity=0.35),
                Chord("G", "maj7", 3 if inst != "cello" else 2, duration=BAR * 2, velocity=0.38),
                Chord("D", "maj7", 3 if inst != "cello" else 2, duration=BAR * 4, velocity=0.35),
            ],
            0.1,
            0.65,
        )
    )

song._effects = {
    "pad": lambda s, sr: stereo_width(conv_reverb(s, sr, room="hall", wet=0.45), width=1.9),
    "guitar": lambda s, sr: delay(
        conv_reverb(s, sr, room="chamber", wet=0.3),
        sr,
        delay_ms=441.0,
        feedback=0.35,
        wet=0.2,
    ),
    "violin": lambda s, sr: conv_reverb(s, sr, room="hall", wet=0.35),
    "strings": lambda s, sr: conv_reverb(s, sr, room="hall", wet=0.33),
    "cello": lambda s, sr: conv_reverb(s, sr, room="hall", wet=0.35),
}
