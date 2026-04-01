"""dub_reggae.py — Dub reggae. Gm, 74 BPM. Lee Perry space echo vibes.

Deep dub with echo-drenched drums, heavy sub bass, and sparse melodica.
Uses EffectsChain with heavy delay feedback for authentic dub sound.

Style: Dub reggae, Gm, 74 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, highpass, lowpass, reverb

song = Song(title="Dub Reggae", bpm=74)
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
snare = song.add_track(Track(name="rimshot", instrument="drums_snare", volume=0.45))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.25))
for _ in range(12):
    kick.extend([Note("C", 2, 1.5), r(0.5), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.5), Note("E", 4, 0.5), r(1.5), Note("E", 4, 0.5)])
    hat.extend([Note("F#", 6, 0.5)] * 8)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.65))
for _ in range(12):
    bass.extend([Note("G", 2, 1.5), Note("G", 2, 0.5), r(1.0), Note("Bb", 2, 1.0)])

organ = song.add_track(Track(name="skank", instrument="organ", volume=0.3, pan=0.2))
for _ in range(12):
    organ.extend([r(0.5), Chord("G", "min", 4, duration=0.5), r(0.5), Chord("G", "min", 4, duration=0.5),
                  r(0.5), Chord("G", "min", 4, duration=0.5), r(0.5), Chord("G", "min", 4, duration=0.5)])

melodica = song.add_track(Track(name="melodica", instrument="triangle", volume=0.4, pan=-0.2))
for _ in range(6):
    melodica.extend([Note("Bb", 5, 1.0), Note("G", 5, 0.5), Note("D", 5, 0.5), r(2.0),
                     Note("F", 5, 0.5), Note("Eb", 5, 0.5), Note("D", 5, 1.0), r(2.0)])

song.effects = {
    "rimshot": EffectsChain().add(delay, delay_ms=405, feedback=0.45, wet=0.35).add(reverb, room_size=0.6, wet=0.3),
    "bass": EffectsChain().add(lowpass, cutoff_hz=200),
    "melodica": EffectsChain().add(delay, delay_ms=810, feedback=0.35, wet=0.25),
    "skank": EffectsChain().add(highpass, cutoff_hz=500),
}
