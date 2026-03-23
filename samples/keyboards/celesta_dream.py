"""Celesta dream: Tchaikovsky Sugar Plum territory, D major, 76 BPM.

Alluring. The celesta sounds like a child's idea of magic.
Used in horror (The Shining), used in wonder (Fantasia).
Here it's purely wonder — a melody that sounds like stars.
"""

from code_music import Note, Song, Track, delay, humanize, reverb, stereo_width

song = Song(title="celesta_dream", bpm=76)

cel = song.add_track(Track(name="celesta", instrument="celesta", volume=0.78, pan=0.0))

dream = humanize(
    [
        Note("F#", 6, 0.5),
        Note("E", 6, 0.25),
        Note("D", 6, 0.25),
        Note("C#", 6, 1.0),
        Note("B", 5, 0.5),
        Note("A", 5, 0.5),
        Note("F#", 5, 1.5),
        Note.rest(0.5),
        Note("G", 5, 0.25),
        Note("A", 5, 0.25),
        Note("B", 5, 0.5),
        Note("D", 6, 0.5),
        Note("C#", 6, 0.5),
        Note("B", 5, 0.5),
        Note("A", 5, 2.0),
        Note.rest(1.5),
        Note("A", 6, 0.5),
        Note("F#", 6, 0.5),
        Note("D", 6, 1.0),
        Note("E", 6, 0.5),
        Note("C#", 6, 0.5),
        Note("A", 5, 1.0),
        Note("F#", 5, 4.0),
    ],
    vel_spread=0.08,
    timing_spread=0.05,
)
cel.extend(dream)

# Faint pad underneath — just barely there
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.2, pan=0.0))
for ch, sh in [("D", "maj7"), ("A", "maj7"), ("B", "min7"), ("G", "maj7")]:
    pad.extend([Note(ch, 3, 4.0, velocity=0.3)])

song._effects = {
    "celesta": lambda s, sr: stereo_width(
        delay(reverb(s, sr, room_size=0.75, wet=0.35), sr, delay_ms=789.0, feedback=0.2, wet=0.12),
        width=1.4,
    ),
    "pad": lambda s, sr: reverb(s, sr, room_size=0.9, wet=0.5),
}
