"""Dawn break: rising strings + piano, E major, the moment sun clears the horizon.

Energizing. Not aggressive — pure lift. Strings crescendo from nothing,
piano leads the charge upward. By the end you want to move.
"""

from code_music import Note, Song, Track, crescendo, humanize, reverb, stereo_width

song = Song(title="dawn_break", bpm=96)

# Strings swell from pianissimo
for inst, pan_v, offset in [("violin", -0.4, 0), ("strings", -0.1, 1), ("cello", 0.35, 2)]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=0.65, pan=pan_v))
    tr.extend([Note.rest(offset * 2.0)])
    rising = [
        Note("E", 4 if inst != "cello" else 3, 1.0),
        Note("F#", 4 if inst != "cello" else 3, 1.0),
        Note("G#", 4 if inst != "cello" else 3, 1.0),
        Note("B", 4 if inst != "cello" else 3, 1.0),
        Note("C#", 5 if inst != "cello" else 4, 2.0),
        Note("E", 5 if inst != "cello" else 4, 2.0),
        Note("B", 4 if inst != "cello" else 3, 1.0),
        Note("G#", 4 if inst != "cello" else 3, 1.0),
        Note("E", 5 if inst != "cello" else 4, 4.0),
    ]
    tr.extend(humanize(crescendo(rising, start_vel=0.1, end_vel=0.9), vel_spread=0.04))

# Piano drives up through the texture
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.75, pan=0.1))
piano.extend([Note.rest(4.0)])
lead = crescendo(
    [
        Note("E", 5, 0.5),
        Note("F#", 5, 0.5),
        Note("G#", 5, 1.0),
        Note("B", 5, 0.5),
        Note("C#", 6, 0.5),
        Note("E", 6, 2.0),
        Note("C#", 6, 0.5),
        Note("B", 5, 0.5),
        Note("G#", 5, 1.0),
        Note("E", 5, 0.5),
        Note("F#", 5, 0.5),
        Note("G#", 5, 0.5),
        Note("B", 5, 0.5),
        Note("E", 6, 4.0),
    ],
    0.4,
    1.0,
)
piano.extend(lead)

song._effects = {
    "violin": lambda s, sr: reverb(s, sr, room_size=0.75, wet=0.28),
    "strings": lambda s, sr: reverb(s, sr, room_size=0.75, wet=0.28),
    "cello": lambda s, sr: reverb(s, sr, room_size=0.8, wet=0.3),
    "piano": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.6, wet=0.2), width=1.3),
}
