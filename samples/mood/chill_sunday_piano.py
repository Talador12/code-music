"""Sunday morning piano: Cmaj7 - Fmaj7, rubato, unhurried, alone.

Chill. Playing for no one. The kind of piano playing that happens
when you're not trying to make music, you're just moving your hands.
Some notes sustain longer than they should. That's the point.
"""

from code_music import Note, Song, Track, chorus, humanize, reverb

song = Song(title="sunday_piano", bpm=74)

piano = song.add_track(Track(name="piano", instrument="piano", volume=0.75, pan=0.0))

# Right hand: melody with long sustains
rh = humanize(
    [
        Note("E", 5, 1.5),
        Note("D", 5, 0.5),
        Note("C", 5, 2.0),
        Note.rest(0.5),
        Note("G", 4, 0.5),
        Note("A", 4, 0.5),
        Note("B", 4, 0.5),
        Note("C", 5, 3.0),
        Note.rest(1.0),
        Note("F", 5, 1.0),
        Note("E", 5, 0.5),
        Note("D", 5, 0.5),
        Note("C", 5, 0.5),
        Note("B", 4, 0.5),
        Note("A", 4, 1.0),
        Note("G", 4, 4.0),
        Note.rest(1.0),
        Note("A", 4, 1.0),
        Note("B", 4, 0.5),
        Note("C", 5, 0.5),
        Note("E", 5, 2.0),
        Note("D", 5, 1.0),
        Note("C", 5, 3.0),
    ],
    vel_spread=0.09,
    timing_spread=0.05,
)
piano.extend(rh)

song._effects = {
    "piano": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.55, wet=0.22),
        sr,
        rate_hz=0.3,
        depth_ms=1.5,
        wet=0.08,
    ),
}
