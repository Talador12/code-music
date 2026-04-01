"""afrobeat_groove.py — Afrobeat. Gm, 112 BPM. Fela Kuti meets Tony Allen.

Polyrhythmic drums, driving bass, and horn-like synth stabs over a
hypnotic groove. Uses Track.loop for the repeating drum pattern.

Style: Afrobeat, Gm, 112 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, compress, reverb

song = Song(title="Afrobeat Groove", bpm=112)
r = Note.rest

kick_bar = Track(name="kick", instrument="drums_kick", volume=0.75)
kick_bar.extend([Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5), r(1.0), Note("C", 2, 1.0)])
song.add_track(kick_bar.loop(20))

snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.4))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3))
for _ in range(20):
    snare.extend([r(0.75), Note("E", 4, 0.25), r(0.5), Note("E", 4, 0.25), Note("E", 4, 0.25),
                  r(0.5), Note("E", 4, 0.25), r(0.5), Note("E", 4, 0.25), r(0.25), Note("E", 4, 0.25)])
    hat.extend([Note("F#", 6, 0.25)] * 16)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
bass_riff = [Note("G", 2, 0.5), r(0.5), Note("G", 2, 0.5), Note("Bb", 2, 0.5),
             Note("C", 3, 0.5), Note("Bb", 2, 0.5), Note("G", 2, 0.5), r(0.5)]
for _ in range(20):
    bass.extend(bass_riff)

horns = song.add_track(Track(name="horns", instrument="sawtooth", volume=0.45, pan=0.15))
for _ in range(10):
    horns.extend([r(4.0), Note("Bb", 4, 0.5), Note("D", 5, 0.5), Note("G", 5, 1.0),
                  Note("F", 5, 0.5), Note("D", 5, 0.5), Note("Bb", 4, 1.0)])

keys = song.add_track(Track(name="keys", instrument="organ", volume=0.3, pan=-0.2))
for _ in range(10):
    keys.extend([Chord("G", "min7", 3, duration=4.0), Chord("C", "min7", 3, duration=4.0)])

song.effects = {
    "horns": EffectsChain().add(reverb, room_size=0.4, wet=0.15).add(compress, threshold=0.5, ratio=3.0),
    "keys": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
}
