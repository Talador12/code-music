"""Harp at dawn: solo harp, F major pentatonic, 63 BPM.

Chill. That specific quality of light before 7am.
Arpeggiated chords that rise and fall like breath.
Nothing urgent. Nothing demands your attention.
"""

from code_music import Chord, Note, Song, Track, arp, reverb, stereo_width

song = Song(title="harp_dawn", bpm=63)

harp = song.add_track(Track(name="harp", instrument="harp", volume=0.78, pan=0.0))

# Slow rolling arpeggios, very unhurried
for ch, sh, vel in [
    ("F", "maj7", 0.55),
    ("C", "maj", 0.5),
    ("A", "min7", 0.52),
    ("G", "dom7", 0.5),
    ("F", "maj7", 0.55),
    ("D", "min7", 0.5),
    ("C", "sus2", 0.52),
    ("F", "maj", 0.6),
]:
    notes = arp(Chord(ch, sh, 4, velocity=vel), pattern="up", rate=0.5, octaves=2)
    harp.extend(notes)
    harp.add(Note.rest(2.0))

song.effects = {
    "harp": lambda s, sr: stereo_width(
        reverb(s, sr, room_size=0.8, damping=0.4, wet=0.35),
        width=1.6,
    ),
}
