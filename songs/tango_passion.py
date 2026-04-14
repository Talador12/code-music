"""tango_passion.py - Argentine tango. A harmonic minor, 132 BPM.

Dramatic harmonic minor melody with bandoneon-style pad, staccato
bass, and a habanera-like rhythm. Buenos Aires in the rain.

Style: Tango, A harmonic minor, 132 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale

song = Song(title="Tango Passion", bpm=132, sample_rate=44100)
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.65))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.4))
for _ in range(16):
    kick.extend([Note("C", 2, 1.5), Note("C", 2, 0.5), Note("C", 2, 1.0), Note("C", 2, 1.0)])
    snare.extend([r(1.5), Note("E", 4, 0.5), r(1.0), Note("E", 4, 0.5), r(0.5)])

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
for _ in range(16):
    bass.extend(
        [
            Note("A", 2, 0.5),
            r(0.5),
            Note("E", 2, 0.5),
            r(0.5),
            Note("A", 2, 0.5),
            Note("C", 3, 0.5),
            Note("B", 2, 0.5),
            r(0.5),
        ]
    )

bandoneon = song.add_track(Track(name="bandoneon", instrument="organ", volume=0.4, pan=-0.1))
for _ in range(4):
    bandoneon.extend(
        [
            Chord("A", "min", 3, duration=4.0),
            Chord("E", "dom7", 3, duration=4.0),
            Chord("D", "min", 3, duration=4.0),
            Chord("E", "dom7", 3, duration=4.0),
        ]
    )

melody = song.add_track(Track(name="melody", instrument="sawtooth", volume=0.45, pan=0.1))
notes = scale("A", "harmonic_minor", octave=5, length=8)
for _ in range(8):
    for i in range(0, 7, 2):
        melody.add(Note(notes[i].pitch, notes[i].octave, 0.5))
    melody.add(Note(notes[6].pitch, notes[6].octave, 1.0))
    melody.add(r(2.5))

song.effects = {
    "bandoneon": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
    "melody": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
}
