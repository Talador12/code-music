"""Pattern Chain — jazz licks chained together with connectors."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import chain_patterns

song = Song(title="Pattern Chain", bpm=140)

# Chain jazz licks
licks = chain_patterns(
    ["jazz_ii_v_i", "jazz_enclosure", "jazz_bebop_turn", "jazz_blues_head"],
    key="Bb",
    octave=5,
    duration=0.25,
)

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=0.15))
lead.extend(licks)

comp = song.add_track(Track(name="comp", instrument="piano", volume=0.35, pan=-0.1))
comp.add(Chord("Bb", "maj7", 3, duration=8.0))
comp.add(Chord("Eb", "maj7", 3, duration=8.0))

song.effects = {
    "lead": EffectsChain().add(delay, delay_ms=200, feedback=0.15, wet=0.1),
    "comp": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
}
