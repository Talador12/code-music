"""gospel_praise.py — Gospel. Bb major, 88 BPM. Sunday morning choir energy.

Hammond organ chords, walking bass, and a call-and-response melody.
Uses Track.merge to layer organ voicings.

Style: Gospel, Bb major, 88 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, stereo_width

song = Song(title="Gospel Praise", bpm=88)

r = Note.rest

organ_left = Track(name="organ", instrument="organ", volume=0.45, pan=-0.2)
organ_right = Track(name="organ", instrument="organ", volume=0.45, pan=-0.2)
for _ in range(8):
    organ_left.extend(
        [
            Chord("Bb", "maj7", 3, duration=4.0),
            Chord("Eb", "maj", 3, duration=4.0),
        ]
    )
    organ_right.extend(
        [
            r(2.0),
            Chord("Bb", "maj7", 4, duration=2.0),
            r(2.0),
            Chord("Eb", "maj", 4, duration=2.0),
        ]
    )
song.add_track(organ_left.merge(organ_right))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
for _ in range(8):
    bass.extend(
        [
            Note("Bb", 2, 1.0),
            Note("D", 3, 1.0),
            Note("F", 3, 1.0),
            Note("D", 3, 1.0),
            Note("Eb", 2, 1.0),
            Note("G", 2, 1.0),
            Note("Bb", 2, 1.0),
            Note("G", 2, 1.0),
        ]
    )

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15))
for _ in range(8):
    lead.extend(
        [
            Note("D", 5, 0.5),
            Note("F", 5, 0.5),
            Note("Bb", 5, 1.0),
            Note("A", 5, 0.5),
            Note("F", 5, 0.5),
            Note("D", 5, 1.0),
            Note("Eb", 5, 0.5),
            Note("G", 5, 0.5),
            Note("Bb", 5, 1.0),
            Note("F", 5, 1.0),
            r(1.0),
        ]
    )

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.65))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.45))
for _ in range(16):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)])

song.effects = {
    "organ": EffectsChain().add(reverb, room_size=0.6, wet=0.3).add(stereo_width, width=1.4),
    "lead": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
}
