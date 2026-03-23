"""Full orchestra swell: C major chord from pp to ff, all sections.

Layers in order: strings → woodwinds → brass → timpani crash.
"""

from code_music import Chord, Note, Song, Track

song = Song(title="full_orchestra_swell", bpm=72)

# Strings — long swell
for inst, pan_v, vol in [("strings", -0.3, 0.6), ("cello", 0.3, 0.65), ("contrabass", 0.1, 0.6)]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=vol, pan=pan_v))
    for _ in range(4):
        tr.add(Chord("C", "maj", 3, duration=4.0, velocity=0.4 + _ * 0.15))

# Woodwinds enter bar 3
for inst, pan_v in [("flute", -0.4), ("oboe", -0.1), ("clarinet", 0.1), ("bassoon", 0.4)]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=0.6, pan=pan_v))
    tr.add(Note.rest(8.0))
    for _ in range(2):
        tr.add(
            Chord(
                "C",
                "maj",
                4 if inst in ("flute", "oboe") else 3,
                duration=4.0,
                velocity=0.55 + _ * 0.15,
            )
        )

# Brass enter bar 4
for inst, pan_v in [("trumpet", -0.3), ("french_horn", 0.0), ("trombone", 0.3)]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=0.75, pan=pan_v))
    tr.add(Note.rest(12.0))
    tr.add(Chord("C", "maj", 4, duration=4.0, velocity=0.85))

# Timpani crash at the peak
timp = song.add_track(Track(name="timpani", instrument="timpani", volume=0.9))
timp.add(Note.rest(12.0))
timp.add(Note("C", 2, 4.0, velocity=1.0))
