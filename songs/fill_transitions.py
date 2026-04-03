"""Fill Transitions — drum fills and risers between sections."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.composition import generate_fill, generate_riser

song = Song(title="Fill Transitions", bpm=120, sample_rate=44100)
song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7)).extend(
    [Note("C", 2, 1.0) for _ in range(8)]
)
# Snare fill transition
song.add_track(Track(name="fill", instrument="drums_snare", volume=0.6)).extend(
    [Note.rest(1.0)] * 7 + generate_fill(bars=1, style="snare_roll")
)
# Riser
song.add_track(Track(name="riser", instrument="sawtooth", volume=0.3)).extend(
    generate_riser(bars=2, start_note="C", octave=3)
)
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).extend(
    [Chord("C", "min7", 3, duration=8.0)]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
