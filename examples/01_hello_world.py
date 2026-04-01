"""01 — Hello World: the simplest possible song.

Run:  code-music examples/01_hello_world.py --play
"""

from code_music import Note, Song, Track

# Every song starts with a Song object
song = Song(title="Hello World", bpm=120)

# Add a track with an instrument
melody = song.add_track(Track(name="melody", instrument="piano"))

# Add some notes: Note(pitch, octave, duration_in_beats)
melody.add(Note("C", 4, 1.0))  # middle C, 1 beat
melody.add(Note("E", 4, 1.0))  # E4
melody.add(Note("G", 4, 1.0))  # G4
melody.add(Note("C", 5, 2.0))  # C5, held for 2 beats

# That's it! Render with: code-music examples/01_hello_world.py -o hello.wav
