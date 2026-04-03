"""Range Analysis — shows note range of different melodies."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import note_range, rhythmic_density

melody = [
    Note(n, o, 0.5)
    for n, o in [("C", 4), ("E", 4), ("G", 4), ("C", 5), ("E", 5), ("G", 5), ("C", 6), ("G", 5)]
]
r = note_range(melody)
d = rhythmic_density(melody)
print(f"Range: {r['lowest']} → {r['highest']} ({r['span_semitones']} semitones)")
print(f"Density: {d['notes_per_beat']} notes/beat")
song = Song(title="Range Analysis", bpm=120, sample_rate=44100)
song.add_track(Track(name="lead", instrument="piano", volume=0.5)).extend(melody)
song.effects = {}
