"""Five Against Four — 5:4 polyrhythm in a jazz-influenced context."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import generate_polyrhythm

song = Song(title="Five Against Four", bpm=96)

# 5:4 polyrhythm — this is the West African heartbeat
voice_a, voice_b = generate_polyrhythm("D", octave=3, rhythm_a=5, rhythm_b=4, bars=4)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55, pan=0.0))
bass.extend(voice_a)

ride = song.add_track(Track(name="ride", instrument="drums_hat", volume=0.3, pan=0.2))
ride.extend(voice_b)

# Chord pad underneath
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35, pan=-0.15))
pad.add(Chord("D", "min9", 3, duration=8.0))
pad.add(Chord("G", "dom7", 3, duration=8.0))

# Melody floating above the polyrhythm
mel = song.add_track(Track(name="melody", instrument="piano", volume=0.5, pan=0.1))
mel.extend(
    [
        Note("D", 5, 1.5),
        Note("F", 5, 0.5),
        Note("A", 5, 1.0),
        Note("G", 5, 1.0),
        Note("F", 5, 2.0),
        Note("E", 5, 1.0),
        Note("D", 5, 1.0),
        Note("C", 5, 2.0),
        Note("D", 5, 1.0),
        Note("F", 5, 1.0),
        Note("A", 5, 2.0),
        Note("G", 5, 1.0),
        Note("F", 5, 1.0),
    ]
)

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
    "melody": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
}
