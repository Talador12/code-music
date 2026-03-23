"""Music box memory: celesta, C major, 66 BPM. Childhood. Nostalgia. Distance.

Chill. A music box playing in another room.
The high frequencies have that slight wind-down quality. Very alone.
Every note is a small, complete thing.
"""

from code_music import Note, Song, Track, delay, humanize, reverb

song = Song(title="music_box_memory", bpm=66)

box = song.add_track(Track(name="box", instrument="celesta", volume=0.72, pan=0.0))

# A simple melody that sounds like something half-remembered
mel = humanize(
    [
        Note("E", 6, 0.5),
        Note("G", 6, 0.5),
        Note("C", 7, 1.0),
        Note("B", 6, 0.5),
        Note("A", 6, 0.5),
        Note("G", 6, 1.0),
        Note("E", 6, 0.5),
        Note("F", 6, 0.5),
        Note("G", 6, 0.5),
        Note("A", 6, 0.5),
        Note("G", 6, 2.0),
        Note.rest(1.0),
        Note("D", 6, 0.5),
        Note("E", 6, 0.5),
        Note("F", 6, 0.5),
        Note("G", 6, 0.5),
        Note("A", 6, 1.0),
        Note("G", 6, 0.5),
        Note("E", 6, 0.5),
        Note("C", 6, 4.0),
        Note.rest(2.0),
        Note("G", 6, 0.5),
        Note("E", 6, 0.5),
        Note("C", 6, 3.0),
    ],
    vel_spread=0.08,
    timing_spread=0.06,
)

box.extend(mel)

song._effects = {
    "box": lambda s, sr: delay(
        reverb(s, sr, room_size=0.7, damping=0.5, wet=0.3),
        sr,
        delay_ms=720.0,
        feedback=0.25,
        wet=0.15,
    ),
}
