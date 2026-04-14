"""indian_raga.py - Indian raga. D hirajoshi, 70 BPM.

Meditative drone on D with a hirajoshi-scale melody floating above.
Tanpura-like pad holds steady while the sitar-like lead wanders.

Style: Raga, D hirajoshi, 70 BPM.
"""

from code_music import EffectsChain, Note, Song, Track, delay, reverb, scale

song = Song(title="Indian Raga", bpm=70, sample_rate=44100)
r = Note.rest

drone = song.add_track(Track(name="drone", instrument="pad", volume=0.4))
drone.extend([Note("D", 3, 4.0)] * 16)

drone_fifth = song.add_track(Track(name="drone_fifth", instrument="pad", volume=0.25, pan=0.1))
drone_fifth.extend([Note("A", 3, 4.0)] * 16)

melody = song.add_track(Track(name="melody", instrument="triangle", volume=0.5, pan=-0.15))
notes = scale("D", "hirajoshi", octave=5, length=5)
phrases = [
    [notes[0], notes[2], notes[4], r(0.5), notes[3], notes[1], notes[0], r(1.0)],
    [notes[1], notes[3], notes[4], r(0.5), notes[2], notes[0], r(1.5)],
]
for i in range(8):
    for n in phrases[i % 2]:
        if hasattr(n, "pitch") and n.pitch is not None:
            melody.add(Note(n.pitch, n.octave, 0.75))
        else:
            melody.add(n)
    melody.add(r(2.0))

tabla = song.add_track(Track(name="tabla", instrument="drums_kick", volume=0.5))
tabla_hi = song.add_track(Track(name="tabla_hi", instrument="drums_hat", volume=0.3))
for _ in range(16):
    tabla.extend([Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5), r(1.0), Note("C", 2, 1.0)])
    tabla_hi.extend([r(0.25), Note("F#", 6, 0.25)] * 8)

song.effects = {
    "melody": EffectsChain()
    .add(delay, delay_ms=428, feedback=0.25, wet=0.2)
    .add(reverb, room_size=0.6, wet=0.3),
    "drone": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
}
