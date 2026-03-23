"""Phrygian pad: E Phrygian, slow supersaw, 55 BPM. Ancient. Inevitable.

Alluring. Phrygian mode has a flatted second degree that creates
permanent unease — it never fully resolves. A slow pull toward something
you can't name. Used in flamenco, metal, middle-eastern music.
Here it floats.
"""

from code_music import Chord, Note, Song, Track, arp, lfo_filter, phaser, reverb, stereo_width

song = Song(title="phrygian_pad", bpm=55)

# Phrygian chords: Em - F - Dm - Am (that F natural is the key)
pad = song.add_track(Track(name="pad", instrument="supersaw", volume=0.5, pan=0.0))
for ch, sh, dur in [
    ("E", "min7", 6.0),
    ("F", "maj7", 6.0),
    ("D", "min7", 6.0),
    ("A", "min", 6.0),
    ("E", "min", 6.0),
    ("F", "maj", 6.0),
]:
    pad.add(Chord(ch, sh, 3, duration=dur, velocity=0.55))

# Arp: unhurried, one note every beat
arp_tr = song.add_track(Track(name="arp", instrument="pluck", volume=0.38, pan=0.2))
for ch, sh in [("E", "min"), ("F", "maj"), ("D", "min"), ("A", "min"), ("E", "min"), ("F", "maj")]:
    arp_tr.extend(arp(Chord(ch, sh, 4), pattern="up", rate=1.0))

# A lone melody fragment, barely present
mel = song.add_track(Track(name="mel", instrument="flute", volume=0.4, pan=-0.2))
mel.extend(
    [
        Note.rest(6.0),
        Note("E", 5, 2.0),
        Note("F", 5, 1.0),
        Note.rest(3.0),
        Note("D", 5, 2.0),
        Note("E", 5, 4.0),
        Note.rest(6.0),
        Note("A", 4, 2.0),
        Note("B", 4, 1.0),
        Note("C", 5, 1.0),
        Note("B", 4, 2.0),
        Note("E", 5, 6.0),
    ]
)

song._effects = {
    "pad": lambda s, sr: stereo_width(
        lfo_filter(
            reverb(s, sr, room_size=0.8, wet=0.35),
            sr,
            rate_hz=0.04,
            min_cutoff=250.0,
            max_cutoff=5000.0,
        ),
        width=1.9,
    ),
    "arp": lambda s, sr: phaser(reverb(s, sr, room_size=0.6, wet=0.2), sr, rate_hz=0.15, wet=0.3),
    "mel": lambda s, sr: reverb(s, sr, room_size=0.85, wet=0.4),
}
