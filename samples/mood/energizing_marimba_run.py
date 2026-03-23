"""Marimba run: fast sixteenth-note patterns, G major, 132 BPM. Pure joy.

Energizing. Marimba at speed is unstoppable — it just goes.
Light, bright, percussive. The physical pleasure of fast hands.
"""

from code_music import Note, Song, Track, crescendo, humanize, reverb

song = Song(title="marimba_run", bpm=132)

mar = song.add_track(Track(name="marimba", instrument="marimba", volume=0.8, pan=0.0))

# Classic marimba run pattern: scale fragments + arpeggios
run_a = [
    Note("G", 5, 0.25),
    Note("A", 5, 0.25),
    Note("B", 5, 0.25),
    Note("D", 6, 0.25),
    Note("C", 6, 0.25),
    Note("B", 5, 0.25),
    Note("A", 5, 0.25),
    Note("G", 5, 0.25),
]
run_b = [
    Note("D", 5, 0.25),
    Note("F#", 5, 0.25),
    Note("A", 5, 0.25),
    Note("D", 6, 0.25),
    Note("C", 6, 0.25),
    Note("A", 5, 0.25),
    Note("F#", 5, 0.25),
    Note("D", 5, 0.25),
]
run_c = [
    Note("E", 5, 0.25),
    Note("G", 5, 0.25),
    Note("B", 5, 0.25),
    Note("E", 6, 0.25),
    Note("D", 6, 0.25),
    Note("B", 5, 0.25),
    Note("G", 5, 0.25),
    Note("E", 5, 0.25),
]
landing = [Note("G", 5, 1.0), Note("B", 5, 0.5), Note("D", 6, 0.5), Note("G", 6, 2.0)]

full = (run_a + run_b) * 2 + run_c * 2 + run_a + run_b
mar.extend(humanize(crescendo(full, 0.55, 0.9), vel_spread=0.06))
mar.extend(humanize(landing, vel_spread=0.03))

song._effects = {
    "marimba": lambda s, sr: reverb(s, sr, room_size=0.5, wet=0.18),
}
