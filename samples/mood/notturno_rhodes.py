"""Late night rhodes: just rhodes and contrabass, 3am and alone.

Chill. No drums. Space between notes matters as much as the notes.
Gm7 - Eb maj7 - Bb - F — the jazz chords that sound like fog.
"""

from code_music import Chord, Note, Song, Track, chorus, reverb

song = Song(title="late_night_rhodes", bpm=72)

bass = song.add_track(Track(name="bass", instrument="contrabass", volume=0.65, pan=0.1))
comp = song.add_track(Track(name="comp", instrument="rhodes", volume=0.7, pan=-0.15, swing=0.48))

bass_walk = [
    Note("G", 2, 2.0),
    Note("F", 2, 1.0),
    Note("D#", 2, 1.0),
    Note("D#", 2, 2.0),
    Note("F", 2, 2.0),
    Note("A#", 1, 2.0),
    Note("D", 2, 2.0),
    Note("F", 2, 2.0),
    Note("C", 2, 1.0),
    Note("D", 2, 1.0),
    Note("G", 2, 4.0),
]
comp_chords = [
    Chord("G", "min7", 3, duration=4.0, velocity=0.55),
    Chord("D#", "maj7", 3, duration=4.0, velocity=0.5),
    Chord("A#", "maj7", 3, duration=4.0, velocity=0.52),
    Chord("F", "dom7", 3, duration=4.0, velocity=0.5),
]

for _ in range(2):
    bass.extend(bass_walk)
    comp.extend(comp_chords)

song.effects = {
    "comp": lambda s, sr: chorus(reverb(s, sr, room_size=0.5, wet=0.2), sr, rate_hz=0.5, wet=0.15),
    "bass": lambda s, sr: reverb(s, sr, room_size=0.4, wet=0.12),
}
