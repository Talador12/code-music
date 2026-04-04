"""Contour Arch — generated melody with arch contour over a chord pad."""

from code_music import Chord, EffectsChain, Song, Track, delay, reverb
from code_music.theory import generate_rhythm_pattern, generate_scale_melody

song = Song(title="Contour Arch", bpm=100)

# Arch melody in D dorian
melody = generate_scale_melody(
    key="D",
    scale_name="dorian",
    length=32,
    octave=5,
    duration=0.5,
    contour="arch",
    seed=42,
)

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=0.15))
lead.extend(melody)

# Rhythm pattern underneath
rhythm_notes = generate_rhythm_pattern(hits=6, slots=16, note="D", octave=3, seed=7)
perc = song.add_track(Track(name="perc", instrument="pluck", volume=0.35, pan=-0.1))
perc.extend(rhythm_notes * 2)

# Chord pad
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35, pan=-0.15))
pad.add(Chord("D", "min7", 3, duration=8.0))
pad.add(Chord("G", "dom7", 3, duration=8.0))

song.effects = {
    "lead": EffectsChain().add(delay, delay_ms=300, feedback=0.2, wet=0.15),
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
}
