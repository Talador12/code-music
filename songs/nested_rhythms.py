"""Nested Rhythms — quintuplets inside triplets, plus irrational meters."""

from code_music import EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import irrational_meter, nested_tuplet

song = Song(title="Nested Rhythms", bpm=100)

# Triplets of quintuplets: 3 groups of 5 = 15 notes in 4 beats
source = [Note("E", 5, 1.0)] * 15
nested = nested_tuplet(3, 5, source, total_duration=4.0)
lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.1))
lead.extend(nested)
lead.add(Note.rest(2.0))

# 7/12 irrational meter — 7 beats of triplet subdivision
weird = irrational_meter(7, 12, "D", 4, bars=4)
perc = song.add_track(Track(name="perc", instrument="pluck", volume=0.4, pan=-0.15))
perc.extend(weird)

song.effects = {
    "lead": EffectsChain().add(delay, delay_ms=200, feedback=0.15, wet=0.15),
    "perc": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
}
