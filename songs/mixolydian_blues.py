"""mixolydian_blues.py - Mixolydian mode over bluesy changes. A7 shuffle feel."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb

song = Song(title="Mixolydian Blues", bpm=112, sample_rate=44100)

# Shuffle chords - 12 bar blues in A with dom7s
chords = song.add_track(Track(name="chords", instrument="piano", volume=0.4, pan=-0.2, swing=0.15))
for root in ["A", "A", "A", "A", "D", "D", "A", "A", "E", "D", "A", "E"] * 2:
    chords.add(Chord(root, "dom7", 3, duration=4.0, velocity=50))

# Bass - root-fifth pattern with swing
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6, swing=0.12))
for root in ["A", "A", "A", "A", "D", "D", "A", "A", "E", "D", "A", "E"] * 2:
    for _ in range(2):
        bass.add(Note(root, 2, 1.0, velocity=70))
        bass.add(Note(root, 3, 0.5, velocity=55))
        bass.add(Note.rest(0.5))

# Lead - A mixolydian licks
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=0.25))
lick = [
    Note("A", 4, 0.5),
    Note("C#", 5, 0.5),
    Note("E", 5, 0.75),
    Note("G", 5, 0.25),
    Note("A", 5, 1.0),
    Note("G", 5, 0.5),
    Note("E", 5, 0.5),
    Note("C#", 5, 0.5),
    Note("A", 4, 0.5),
    Note.rest(1.0),
    Note("G", 4, 0.5),
    Note("A", 4, 1.0),
    Note.rest(0.5),
]
lead.extend(lick * 8)

# Kick on 1 and 3
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
for _ in range(48):
    kick.extend([Note("C", 2, 1.0), Note.rest(1.0)])

song.effects = {
    "lead": EffectsChain().add(delay, delay_ms=375.0, feedback=0.25, wet=0.2),
    "chords": EffectsChain().add(reverb, room_size=0.4, wet=0.15),
}
