"""Polyrhythm Lab — 3-against-4 and quintuplet explorations."""

from code_music import EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import generate_polyrhythm, quintuplet, septuplet

song = Song(title="Polyrhythm Lab", bpm=110)

# 3-against-4 polyrhythm
voice_a, voice_b = generate_polyrhythm("C", octave=4, rhythm_a=3, rhythm_b=4, bars=4)

low = song.add_track(Track(name="low", instrument="bass", volume=0.5, pan=-0.3))
low.extend(voice_a)

high = song.add_track(Track(name="high", instrument="pluck", volume=0.45, pan=0.3))
high.extend(voice_b)

# Quintuplet melody
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=0.0))
qnotes = [
    Note("E", 5, 1.0),
    Note("G", 5, 1.0),
    Note("A", 5, 1.0),
    Note("B", 5, 1.0),
    Note("D", 6, 1.0),
]
for _ in range(4):
    lead.extend(quintuplet(qnotes, total_duration=4.0))

# Septuplet fill
fill = song.add_track(Track(name="fill", instrument="piano", volume=0.35, pan=0.15))
snotes = [
    Note("C", 5, 1.0),
    Note("D", 5, 1.0),
    Note("E", 5, 1.0),
    Note("F", 5, 1.0),
    Note("G", 5, 1.0),
    Note("A", 5, 1.0),
    Note("B", 5, 1.0),
]
for _ in range(2):
    fill.extend(septuplet(snotes, total_duration=4.0))
    fill.add(Note.rest(4.0))

song.effects = {
    "lead": EffectsChain().add(delay, delay_ms=200, feedback=0.2, wet=0.15),
    "high": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
}
