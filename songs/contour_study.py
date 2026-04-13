"""Contour Study — analyzes melodic shape of different melodies."""

from code_music import Note, Song, Track
from code_music.theory import melody_contour

asc = [Note(n, o, 0.5) for n, o in [("C", 4), ("E", 4), ("G", 4), ("C", 5)]]
desc = [Note(n, o, 0.5) for n, o in [("C", 5), ("G", 4), ("E", 4), ("C", 4)]]
for name, mel in [("ascending", asc), ("descending", desc)]:
    c = melody_contour(mel)
    print(f"{name}: {c['direction']}, steps={c['steps']}, skips={c['skips']}, leaps={c['leaps']}")
song = Song(title="Contour Study", bpm=100, sample_rate=44100)
song.add_track(Track(name="asc", instrument="piano", volume=0.5, pan=-0.2)).extend(asc)
song.add_track(Track(name="desc", instrument="piano", volume=0.5, pan=0.2)).extend(desc)
song.effects = {}
