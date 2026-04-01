"""Flute morning: solo flute, G Lydian, 72 BPM. Dew on grass. Lightness.

Chill. Lydian mode (major with raised 4th) sounds elevated —
brighter than major, slightly dreaming. A flute in the open air,
not in a concert hall. No accompaniment needed.
"""

from code_music import Note, Song, Track, delay, humanize, reverb

song = Song(title="flute_morning", bpm=72)

fl = song.add_track(Track(name="flute", instrument="flute", volume=0.75, pan=0.0))

# Lydian: G A B C# D E F#
morning = humanize(
    [
        Note("G", 5, 1.0),
        Note("A", 5, 0.5),
        Note("B", 5, 0.5),
        Note("C#", 6, 2.0),
        Note.rest(1.0),
        Note("D", 6, 0.5),
        Note("C#", 6, 0.5),
        Note("B", 5, 0.5),
        Note("A", 5, 0.5),
        Note("G", 5, 3.0),
        Note.rest(1.0),
        Note("E", 5, 0.5),
        Note("F#", 5, 0.5),
        Note("G", 5, 0.5),
        Note("A", 5, 0.5),
        Note("B", 5, 1.0),
        Note("C#", 6, 0.5),
        Note("D", 6, 0.5),
        Note("G", 6, 4.0),
        Note.rest(2.0),
        Note("D", 6, 0.5),
        Note("B", 5, 0.5),
        Note("G", 5, 1.5),
        Note.rest(0.5),
        Note("C#", 6, 1.5),
        Note("A", 5, 0.5),
        Note("G", 5, 4.0),
    ],
    vel_spread=0.07,
    timing_spread=0.04,
)
fl.extend(morning)

song.effects = {
    "flute": lambda s, sr: delay(
        reverb(s, sr, room_size=0.65, damping=0.5, wet=0.25),
        sr,
        delay_ms=416.0,
        feedback=0.2,
        wet=0.1,
    ),
}
