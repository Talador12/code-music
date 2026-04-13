"""DSL Pop Song — a full song written in the mini-DSL notation."""

from code_music import Chord, EffectsChain, Song, Track, delay, reverb
from code_music.theory import song_from_dsl

dsl_text = """
[verse]
chords: | C | Am | F | G |
melody: E5 G5 A5 G5 F5 E5 D5 C5

[chorus]
chords: | F | G | C | Am |
melody: A5 B5 C6 B5 A5 G5 F5 E5

[verse]
chords: | C | Am | F | G |
melody: C5 D5 E5 F5 G5 A5 G5 E5
"""

parsed = song_from_dsl(dsl_text, bpm=120)
song = Song(title="DSL Pop Song", bpm=parsed["bpm"])

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.15))
lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15))

for section in parsed["sections"]:
    for root, shape in section["chords"]:
        pad.add(Chord(root, shape, 3, duration=4.0))
    lead.extend(section["melody"])

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
    "lead": EffectsChain().add(delay, delay_ms=250, feedback=0.15, wet=0.1),
}
