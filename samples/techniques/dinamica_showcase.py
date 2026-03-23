"""Crescendo / decrescendo showcase: strings swell in then out."""

from code_music import Note, Song, Track, crescendo, decrescendo, humanize

song = Song(title="crescendo_showcase", bpm=80)

# Each instrument enters at different dynamics and swells
for inst, pan_v in [("violin", -0.3), ("strings", 0.0), ("cello", 0.3)]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=0.7, pan=pan_v))
    # C minor scale up (crescendo) then down (decrescendo)
    up = humanize(
        crescendo(
            [
                Note("C", 4, 1.0),
                Note("D", 4, 1.0),
                Note("D#", 4, 1.0),
                Note("F", 4, 1.0),
                Note("G", 4, 1.0),
                Note("G#", 4, 1.0),
                Note("A#", 4, 1.0),
                Note("C", 5, 1.0),
            ],
            start_vel=0.15,
            end_vel=0.95,
        ),
        vel_spread=0.03,
    )
    down = humanize(
        decrescendo(
            [
                Note("C", 5, 1.0),
                Note("A#", 4, 1.0),
                Note("G#", 4, 1.0),
                Note("G", 4, 1.0),
                Note("F", 4, 1.0),
                Note("D#", 4, 1.0),
                Note("D", 4, 1.0),
                Note("C", 4, 2.0),
            ],
            start_vel=0.95,
            end_vel=0.1,
        ),
        vel_spread=0.03,
    )
    tr.extend(up + down)
