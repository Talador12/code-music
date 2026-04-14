"""gospel_choir.py - Gospel. Bb major, 88 BPM.

Rich gospel voicings with organ, call-and-response chords,
and a steady tambourine. Sunday morning energy, coded.

Style: Gospel, Bb major, 88 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb

song = Song(title="Gospel Choir", bpm=88, sample_rate=44100)
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.45))
tamb = song.add_track(Track(name="tamb", instrument="drums_hat", volume=0.3))
for _ in range(16):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)])
    tamb.extend([Note("F#", 6, 0.5)] * 8)

organ = song.add_track(Track(name="organ", instrument="organ", volume=0.45))
changes = [
    Chord("Bb", "maj7", 3, duration=4.0),
    Chord("Eb", "maj7", 3, duration=4.0),
    Chord("F", "dom7", 3, duration=4.0),
    Chord("Bb", "maj7", 3, duration=4.0),
    Chord("G", "min7", 3, duration=4.0),
    Chord("C", "min7", 3, duration=4.0),
    Chord("F", "dom7", 3, duration=4.0),
    Chord("Bb", "maj7", 3, duration=4.0),
]
for _ in range(2):
    organ.extend(changes)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
roots = ["Bb", "Eb", "F", "Bb", "G", "C", "F", "Bb"]
for _ in range(2):
    for root in roots:
        bass.extend([Note(root, 2, 2.0), Note(root, 2, 1.0), r(1.0)])

lead = song.add_track(Track(name="lead", instrument="sine", volume=0.4, pan=-0.1))
call = [Note("Bb", 5, 0.5), Note("D", 6, 0.5), Note("F", 6, 1.0), r(2.0)]
for _ in range(8):
    lead.extend(call + [r(4.0)])

song.effects = {
    "organ": EffectsChain().add(reverb, room_size=0.65, wet=0.3),
    "lead": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
}
