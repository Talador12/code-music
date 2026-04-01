"""canon_machine.py — Uses loop + transpose to build a canon from one voice.

A single melodic phrase is looped, then transposed copies enter at
different offsets to create a round/canon. All from one definition.

Style: Minimalist canon, C major, 100 BPM.
"""

from code_music import EffectsChain, Note, Song, Track, reverb, stereo_width

song = Song(title="Canon Machine", bpm=100)

r = Note.rest

# One 4-bar phrase — the seed of the canon
seed = Track(name="voice1", instrument="piano", volume=0.5)
phrase = [
    Note("C", 5, 1.0),
    Note("E", 5, 0.5),
    Note("G", 5, 0.5),
    Note("F", 5, 1.0),
    Note("E", 5, 1.0),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("E", 5, 1.0),
    Note("D", 5, 1.0),
    Note("C", 5, 1.0),
    Note("B", 4, 0.5),
    Note("A", 4, 0.5),
    Note("G", 4, 1.0),
    Note("A", 4, 1.0),
    Note("B", 4, 1.0),
    Note("C", 5, 2.0),
    r(2.0),
]
seed.extend(phrase)

# Voice 1: original, looped 4 times, enters immediately
voice1 = seed.loop(4)
voice1.pan = -0.3
song.add_track(voice1.fade_in(beats=4.0))

# Voice 2: up a 5th, enters 16 beats late
voice2_seed = seed.transpose(7)
voice2_seed.name = "voice2"
voice2_seed.pan = 0.3
voice2 = Track(name="voice2", instrument="piano", volume=0.45, pan=0.3)
voice2.add(r(16.0))  # wait one full phrase
song.add_track(voice2.concat(voice2_seed.loop(3)))

# Voice 3: down an octave, enters 32 beats late
voice3_seed = seed.transpose(-12)
voice3_seed.name = "voice3"
voice3_seed.instrument = "organ"
voice3 = Track(name="voice3", instrument="organ", volume=0.35, pan=0.0)
voice3.add(r(32.0))  # wait two full phrases
song.add_track(voice3.concat(voice3_seed.loop(2)))

# Gentle bass drone
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.4))
for _ in range(16):
    bass.extend([Note("C", 2, 4.0)])

song.effects = {
    "voice1": EffectsChain().add(reverb, room_size=0.55, wet=0.25),
    "voice2": EffectsChain().add(reverb, room_size=0.6, wet=0.28),
    "voice3": EffectsChain().add(reverb, room_size=0.7, wet=0.3).add(stereo_width, width=1.3),
}
