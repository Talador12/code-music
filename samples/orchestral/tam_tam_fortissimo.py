"""Gong crash and cymbal swell: dramatic orchestral impact."""

from code_music import Note, Song, Track

song = Song(title="gong_crash", bpm=60)
gong = song.add_track(Track(name="gong", instrument="gong", volume=0.9))
cymb = song.add_track(Track(name="cymbals", instrument="cymbals", volume=0.75))

gong.add(Note("C", 2, 6.0, velocity=1.0))
cymb.extend([Note("C", 5, 0.25, velocity=0.3 + i * 0.05) for i in range(12)])  # swell in
cymb.add(Note("C", 5, 4.0, velocity=1.0))
