"""town_square.py — RPG town theme via PolyphonicTrack. G major, 110 BPM.

The music that plays when you enter a safe town in a JRPG. Cheerful,
melodic, slightly nostalgic. PolyphonicTrack lets the harp play
rolled chords (each note staggered by a fraction of a beat) while
the flute sings above and a gentle bass walks underneath.

Yasunori Mitsuda (Chrono Trigger), Nobuo Uematsu (FF towns), Koji Kondo.
"""

from code_music import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    WHOLE,
    Note,
    PolyphonicTrack,
    Song,
    Track,
    delay,
    humanize,
    reverb,
)

song = Song(title="Town Square", bpm=110, key_sig="G")

BAR = 4.0
r = Note.rest

# ── PolyphonicTrack harp — rolled chords (staggered note placement) ───────
harp = song.add_polytrack(PolyphonicTrack(name="harp", instrument="harp_ks", volume=0.65, pan=-0.2))


# Rolled chord: each note enters 0.1 beats after the previous
def rolled_chord(root_notes, start_beat, dur=HALF, vel=0.6, spread=0.1):
    for i, (p, o) in enumerate(root_notes):
        harp.add(Note(p, o, dur, velocity=vel - i * 0.03), at=start_beat + i * spread)


# G - C - D - Em progression, rolled
for bar in range(8):
    beat = bar * BAR
    if bar % 4 == 0:
        rolled_chord([("G", 3), ("B", 4), ("D", 5), ("G", 5)], beat)
        rolled_chord([("G", 3), ("B", 4), ("D", 5)], beat + 2.0, dur=QUARTER)
    elif bar % 4 == 1:
        rolled_chord([("C", 3), ("E", 4), ("G", 4), ("C", 5)], beat)
        rolled_chord([("C", 3), ("E", 4), ("G", 4)], beat + 2.0, dur=QUARTER)
    elif bar % 4 == 2:
        rolled_chord([("D", 3), ("F#", 4), ("A", 4), ("D", 5)], beat)
        rolled_chord([("D", 3), ("F#", 4), ("A", 4)], beat + 2.0, dur=QUARTER)
    else:
        rolled_chord([("E", 3), ("G", 4), ("B", 4), ("E", 5)], beat)
        rolled_chord([("E", 3), ("G", 4), ("B", 4)], beat + 2.5, dur=QUARTER)

# ── Flute melody — the town theme ─────────────────────────────────────────
flute = song.add_track(Track(name="flute", instrument="flute", volume=0.62, pan=0.15))

melody = humanize(
    [
        Note("D", 5, QUARTER),
        Note("E", 5, QUARTER),
        Note("G", 5, DOTTED_QUARTER),
        Note("F#", 5, EIGHTH),
        Note("E", 5, HALF),
        Note("D", 5, QUARTER),
        Note("B", 4, QUARTER),
        Note("C", 5, DOTTED_QUARTER),
        Note("D", 5, EIGHTH),
        Note("E", 5, HALF),
        r(QUARTER),
        Note("G", 5, QUARTER),
        Note("A", 5, DOTTED_QUARTER),
        Note("G", 5, EIGHTH),
        Note("F#", 5, QUARTER),
        Note("E", 5, QUARTER),
        Note("D", 5, HALF),
        r(HALF),
        Note("B", 4, QUARTER),
        Note("C", 5, QUARTER),
        Note("D", 5, QUARTER),
        Note("E", 5, QUARTER),
        Note("G", 5, WHOLE),
        r(BAR),
    ],
    vel_spread=0.06,
    timing_spread=0.03,
)
flute.extend(melody)
flute.extend(humanize(melody[: len(melody) // 2], vel_spread=0.05))

# ── Walking bass — gentle ──────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="contrabass", volume=0.55, pan=0.05))
walk = humanize(
    [
        Note("G", 2, 1.0),
        Note("A", 2, 1.0),
        Note("B", 2, 1.0),
        Note("D", 3, 1.0),
        Note("C", 2, 1.0),
        Note("D", 2, 1.0),
        Note("E", 2, 1.0),
        Note("G", 2, 1.0),
        Note("D", 2, 1.0),
        Note("E", 2, 1.0),
        Note("F#", 2, 1.0),
        Note("A", 2, 1.0),
        Note("E", 2, 1.0),
        Note("F#", 2, 1.0),
        Note("G", 2, 1.0),
        Note("B", 2, 1.0),
    ]
    * 2,
    vel_spread=0.06,
    timing_spread=0.02,
)
bass.extend(walk)

# ── Light percussion — tambourine feel ────────────────────────────────────
hat = song.add_track(Track(name="perc", instrument="drums_hat", volume=0.22))
hat.extend([Note("F", 5, EIGHTH, velocity=0.22)] * (8 * 8))

song._effects = {
    "harp": lambda s, sr: reverb(s, sr, room_size=0.55, wet=0.2),
    "flute": lambda s, sr: delay(
        reverb(s, sr, room_size=0.5, wet=0.18), sr, delay_ms=273.0, feedback=0.2, wet=0.1
    ),
    "bass": lambda s, sr: reverb(s, sr, room_size=0.4, wet=0.12),
}
