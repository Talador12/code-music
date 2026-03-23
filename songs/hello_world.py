"""hello_world.py — the simplest code-music song.

A C major scale up and back down, nothing fancy.
Run:
    code-music examples/hello_world.py
"""

from code_music import Song, Track, scale

song = Song(title="Hello World", bpm=100)

melody = song.add_track(Track(name="melody", instrument="sine"))

# Scale up
for note in scale("C", "major", octave=4):
    melody.add(note)

# Scale back down
for note in reversed(scale("C", "major", octave=4)):
    melody.add(note)
