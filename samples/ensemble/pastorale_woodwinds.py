"""Woodwind trio: flute + oboe + clarinet, Eb major, 88 BPM. Pastoral, alive.

Chill. Three woodwinds in open air. Flute on top, oboe in the middle,
clarinet holds the harmonic foundation. The slight intonation differences
between real players creates warmth — humanize approximates that.
"""

from code_music import Note, Song, Track, humanize, reverb

song = Song(title="woodwind_trio", bpm=88)

# Flute: the sparkle
fl_line = humanize(
    [
        Note("D#", 6, 1.0),
        Note("F", 6, 0.5),
        Note("G", 6, 0.5),
        Note("A#", 6, 2.0),
        Note.rest(1.0),
        Note("G", 6, 0.5),
        Note("F", 6, 0.5),
        Note("D#", 6, 0.5),
        Note("C", 6, 0.5),
        Note("D#", 6, 3.0),
        Note.rest(1.0),
        Note("C", 6, 1.0),
        Note("D#", 6, 0.5),
        Note("F", 6, 0.5),
        Note("G", 6, 2.0),
        Note("D#", 6, 2.0),
    ],
    vel_spread=0.06,
    timing_spread=0.04,
)

# Oboe: the warmth
ob_line = humanize(
    [
        Note("G", 5, 1.5),
        Note("A#", 5, 0.5),
        Note("C", 6, 1.0),
        Note("F", 6, 2.0),
        Note.rest(1.0),
        Note("D#", 6, 1.0),
        Note("C", 6, 1.0),
        Note("A#", 5, 2.0),
        Note("G", 5, 3.0),
        Note.rest(1.0),
        Note("A#", 5, 1.0),
        Note("C", 6, 1.0),
        Note("D#", 6, 2.0),
        Note("G", 5, 2.0),
    ],
    vel_spread=0.05,
    timing_spread=0.04,
)

# Clarinet: the foundation
cl_line = humanize(
    [
        Note("D#", 5, 2.0),
        Note("F", 5, 2.0),
        Note("C", 6, 2.0),
        Note("D#", 5, 2.0),
        Note("G", 5, 2.0),
        Note("A#", 5, 2.0),
        Note("D#", 5, 4.0),
    ],
    vel_spread=0.05,
    timing_spread=0.03,
)

for name, inst, line, pan_v in [
    ("flute", "flute", fl_line, -0.3),
    ("oboe", "oboe", ob_line, 0.0),
    ("clarinet", "clarinet", cl_line, 0.3),
]:
    tr = song.add_track(Track(name=name, instrument=inst, volume=0.7, pan=pan_v))
    tr.extend(line)

song._effects = {
    k: lambda s, sr: reverb(s, sr, room_size=0.6, wet=0.2) for k in ("flute", "oboe", "clarinet")
}
