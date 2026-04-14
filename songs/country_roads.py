"""country_roads.py - Country with acoustic guitar feel and simple chords. G major."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb

song = Song(title="Country Roads", bpm=104, sample_rate=44100)

r = Note.rest

# Acoustic guitar chords - simple I-IV-V-I
gtr = song.add_track(Track(name="guitar", instrument="pluck", volume=0.5, pan=-0.1))
prog = [
    Chord("G", "maj", 3, duration=4.0),
    Chord("C", "maj", 3, duration=4.0),
    Chord("D", "maj", 3, duration=4.0),
    Chord("G", "maj", 3, duration=4.0),
]
gtr.extend(prog * 6)

# Bass - country walking bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root in ["G", "C", "D", "G"] * 6:
    bass.extend(
        [
            Note(root, 2, 1.0),
            Note(root, 3, 0.5),
            r(0.5),
            Note(root, 2, 0.5),
            Note(root, 3, 0.5),
            Note(root, 2, 1.0),
        ]
    )

# Melody - simple country tune
lead = song.add_track(Track(name="lead", instrument="piano", volume=0.45, pan=0.2))
verse = [
    Note("G", 4, 1.0),
    Note("A", 4, 0.5),
    Note("B", 4, 1.0),
    Note("D", 5, 0.5),
    r(1.0),
    Note("C", 5, 0.5),
    Note("B", 4, 0.5),
    Note("A", 4, 1.0),
    Note("G", 4, 1.5),
    r(0.5),
    Note("B", 4, 0.5),
    Note("D", 5, 0.5),
    Note("E", 5, 1.0),
    Note("D", 5, 1.0),
    r(0.5),
    Note("B", 4, 0.5),
    Note("A", 4, 0.5),
    Note("G", 4, 1.5),
    r(1.0),
]
lead.extend(verse * 6)

# Drums - train beat
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.55))
for _ in range(24):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend(
        [
            r(0.5),
            Note("D", 3, 0.5),
            r(0.5),
            Note("D", 3, 0.5),
            r(0.5),
            Note("D", 3, 0.5),
            r(0.5),
            Note("D", 3, 0.5),
        ]
    )

song.effects = {
    "guitar": EffectsChain().add(reverb, room_size=0.35, wet=0.12),
    "lead": EffectsChain().add(reverb, room_size=0.3, wet=0.1),
}
