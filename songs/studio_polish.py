"""Studio Polish — jazz trio mastered for streaming platforms."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb
from code_music.mastering import master_audio

song = Song(title="Studio Polish", bpm=95, sample_rate=44100)
song.master()  # existing master chain for EQ + compress + limit

tr_piano = song.add_track(Track(name="piano", instrument="piano", volume=0.5))
prog = [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("A", "min7")]
for root, shape in prog:
    tr_piano.add(Chord(root, shape, 4, duration=4.0))

tr_bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root in ["D", "G", "C", "A"]:
    for note in [root, root, root, root]:
        tr_bass.add(Note(note, 2, 1.0))

tr_ride = song.add_track(Track(name="ride", instrument="drums_hat", volume=0.25))
for _ in range(32):
    tr_ride.add(Note("F#", 6, 0.5))

song.effects = {
    "piano": EffectsChain()
    .add(reverb, room_size=0.5, wet=0.2)
    .add(delay, delay_ms=200, feedback=0.15, wet=0.1)
}
