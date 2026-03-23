"""Timpani roll: sustained tremolo on C and G, battle-march energy."""

from code_music import Note, Song, Track

song = Song(title="timpani_roll", bpm=96)
tr = song.add_track(Track(name="timpani", instrument="timpani", volume=0.9))
# Tremolo = fast repeated notes
for pitch in ["C", "G", "C", "G", "C"]:
    dur = 3.0 if pitch == "C" else 1.0
    tr.extend([Note(pitch, 2, 0.125)] * int(dur / 0.125))
