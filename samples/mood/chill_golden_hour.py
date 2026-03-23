"""Golden hour: acoustic guitar + vibraphone, Bm, late afternoon warmth.

Chill. Sunlight through leaves. The vibraphone shimmers above the guitar
like light on water. Nothing hurries.
"""

from code_music import Chord, Note, Song, Track, arp, chorus, reverb

song = Song(title="golden_hour", bpm=80)

gtr = song.add_track(Track(name="guitar", instrument="guitar_acoustic", volume=0.72, pan=-0.25))
vib = song.add_track(Track(name="vibes", instrument="vibraphone", volume=0.6, pan=0.3))

# Fingerpicked guitar: arp pattern over Bm - G - D - A
for ch, sh in [("B", "min"), ("G", "maj"), ("D", "maj"), ("A", "maj")] * 2:
    gtr.extend(arp(Chord(ch, sh, 3), pattern="up_down", rate=0.5))

# Vibraphone floats above with slow melody
vib_line = [
    Note("B", 5, 1.0),
    Note.rest(0.5),
    Note("D", 6, 0.5),
    Note("F#", 6, 2.0),
    Note.rest(1.0),
    Note("E", 5, 0.5),
    Note("F#", 5, 0.5),
    Note("G", 5, 1.0),
    Note("A", 5, 2.0),
    Note.rest(2.0),
    Note("D", 6, 0.5),
    Note.rest(0.5),
    Note("B", 5, 1.5),
    Note.rest(0.5),
    Note("A", 5, 1.0),
    Note("G", 5, 1.0),
    Note("F#", 5, 2.0),
    Note.rest(4.0),
]
vib.extend(vib_line)

song._effects = {
    "guitar": lambda s, sr: reverb(s, sr, room_size=0.55, wet=0.18),
    "vibes": lambda s, sr: chorus(reverb(s, sr, room_size=0.65, wet=0.3), sr, rate_hz=0.4, wet=0.2),
}
