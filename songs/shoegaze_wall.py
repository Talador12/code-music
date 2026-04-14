"""shoegaze_wall.py - Shoegaze. E major, 98 BPM.

A wall of reverb-drenched guitars, distorted bass, and buried
vocals. My Bloody Valentine would approve (probably not, though).

Style: Shoegaze, E major, 98 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, distortion, reverb

song = Song(title="Shoegaze Wall", bpm=98, sample_rate=44100)
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.6))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.4))
for _ in range(16):
    kick.extend([Note("C", 2, 1.0)] * 4)
    snare.extend([r(1.0), Note("E", 4, 1.0)] * 2)

guitar_l = song.add_track(Track(name="guitar_l", instrument="sawtooth", volume=0.5, pan=-0.4))
guitar_r = song.add_track(Track(name="guitar_r", instrument="sawtooth", volume=0.5, pan=0.4))
chords_l = [Chord("E", "maj", 4, duration=8.0), Chord("B", "maj", 3, duration=8.0)]
chords_r = [Chord("A", "maj", 4, duration=8.0), Chord("E", "maj", 4, duration=8.0)]
for _ in range(4):
    guitar_l.extend(chords_l)
    guitar_r.extend(chords_r)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55))
for _ in range(16):
    bass.extend([Note("E", 2, 2.0), Note("B", 1, 1.0), Note("A", 1, 1.0)])

vocal = song.add_track(Track(name="vocal", instrument="sine", volume=0.3))
for _ in range(8):
    vocal.extend([Note("G#", 4, 2.0), Note("B", 4, 1.0), Note("E", 5, 1.0), r(4.0)])

song.effects = {
    "guitar_l": EffectsChain().add(distortion, drive=0.6).add(reverb, room_size=0.9, wet=0.6),
    "guitar_r": EffectsChain()
    .add(distortion, drive=0.55)
    .add(reverb, room_size=0.85, wet=0.55)
    .add(delay, delay_ms=300, feedback=0.3, wet=0.2),
    "bass": EffectsChain().add(distortion, drive=0.3),
    "vocal": EffectsChain().add(reverb, room_size=0.8, wet=0.5),
}
