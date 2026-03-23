"""Deep bass: low sawtooth A1 with slow attack and strong low-end thump."""

from code_music import Note, Song, Track

song = Song(title="deep_bass", bpm=90)
tr = song.add_track(Track(name="deep_bass", instrument="bass", volume=0.9))
notes = [Note("A", 1, 2.0), Note("G", 1, 1.0), Note("E", 1, 1.0), Note("A", 1, 2.0)]
tr.extend(notes)
