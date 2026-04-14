"""celtic_reel.py - Fast 6/8 Celtic dance tune in G major. Fiddle and flute."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb

song = Song(title="Celtic Reel", bpm=152, time_sig=(6, 8), sample_rate=44100)

r = Note.rest
BAR = 3.0  # 6/8 time: 6 eighth notes = 3 quarter note beats per bar

# Bodhran - strong pulse on 1 and 4
drum = song.add_track(Track(name="bodhran", instrument="drums_kick", volume=0.65))
for _ in range(32):
    drum.extend(
        [
            Note("C", 2, 0.5),
            Note("C", 2, 0.5),
            Note("C", 2, 0.5),
            Note("C", 2, 0.5, velocity=50),
            Note("C", 2, 0.5, velocity=40),
            Note("C", 2, 0.5, velocity=50),
        ]
    )

# Drone bass on G
drone = song.add_track(Track(name="drone", instrument="bass", volume=0.45))
for _ in range(32):
    drone.add(Note("G", 2, BAR))

# Guitar chords
gtr = song.add_track(Track(name="guitar", instrument="pluck", volume=0.4, pan=-0.2))
prog = [
    Chord("G", "maj", 3, duration=BAR),
    Chord("D", "maj", 3, duration=BAR),
    Chord("E", "min", 3, duration=BAR),
    Chord("C", "maj", 3, duration=BAR),
]
gtr.extend(prog * 8)

# Fiddle melody - G major reel
fiddle = song.add_track(Track(name="fiddle", instrument="sawtooth", volume=0.55, pan=0.2))
a = [
    Note("G", 5, 0.5),
    Note("A", 5, 0.5),
    Note("B", 5, 0.5),
    Note("D", 6, 0.5),
    Note("B", 5, 0.5),
    Note("A", 5, 0.5),
]
b = [
    Note("G", 5, 0.5),
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("E", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A", 5, 0.5),
]
c = [
    Note("B", 5, 0.5),
    Note("D", 6, 0.5),
    Note("B", 5, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("F#", 5, 0.5),
]
d = [Note("E", 5, 0.5), Note("D", 5, 0.5), Note("E", 5, 0.5), Note("G", 5, 1.0), r(0.5)]
fiddle.extend((a + b + c + d) * 8)

song.effects = {
    "fiddle": EffectsChain().add(reverb, room_size=0.35, wet=0.15),
    "guitar": EffectsChain().add(reverb, room_size=0.3, wet=0.1),
}
