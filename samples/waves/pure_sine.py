"""Pure sine tone: A4 (440 Hz) reference tone, clean and uncolored."""

from code_music import Note, Song, Track

song = Song(title="pure_sine", bpm=60)
tr = song.add_track(Track(name="sine", instrument="sine", volume=0.7))
tr.add(Note("A", 4, duration=4.0))
