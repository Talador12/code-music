"""reggae_riddim.py - Reggae offbeat skank. Dm, 80 BPM.

Classic one-drop riddim with offbeat organ skank, deep roots bass,
and a rimshot on beat 3. Irie vibrations only.

Style: Roots reggae, Dm, 80 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, highpass, reverb

song = Song(title="Reggae Riddim", bpm=80, sample_rate=44100)
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.75))
rim = song.add_track(Track(name="rimshot", instrument="drums_snare", volume=0.4))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.25))
for _ in range(16):
    kick.extend([r(2.0), Note("C", 2, 1.0), r(1.0)])
    rim.extend([r(2.0), Note("E", 4, 0.5), r(1.5)])
    hat.extend([Note("F#", 6, 0.5)] * 8)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.65))
for _ in range(16):
    bass.extend([Note("D", 2, 1.5), r(0.5), Note("A", 2, 0.5), Note("D", 3, 0.5), r(1.0)])

skank = song.add_track(Track(name="skank", instrument="organ", volume=0.35, pan=0.15))
for _ in range(16):
    skank.extend([r(0.5), Chord("D", "min7", 4, duration=0.5)] * 4)

melody = song.add_track(Track(name="melody", instrument="triangle", volume=0.4, pan=-0.2))
phrase = [
    Note("D", 5, 0.5),
    Note("F", 5, 0.5),
    Note("A", 5, 1.0),
    r(1.0),
    Note("G", 5, 0.5),
    Note("F", 5, 0.5),
    Note("D", 5, 0.5),
    r(0.5),
]
for _ in range(8):
    melody.extend(phrase + [r(4.0)])

song.effects = {
    "rimshot": EffectsChain().add(delay, delay_ms=375, feedback=0.35, wet=0.3),
    "skank": EffectsChain().add(highpass, cutoff_hz=600).add(reverb, room_size=0.3, wet=0.15),
    "melody": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
}
