"""Neapolitan Sunset — dramatic harmonic color from bII chords and augmented sixths."""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    delay,
    reverb,
    scale,
)
from code_music.theory import augmented_sixth, neapolitan_chord, picardy_third

song = Song(title="Neapolitan Sunset", bpm=72)

# Strings pad — harmonic foundation
strings = song.add_track(Track(name="strings", instrument="pad", volume=0.45, pan=-0.1))
strings.add(Chord("C", "min", 3, duration=4.0))
strings.add(Chord("Ab", "maj", 3, duration=4.0))
strings.extend(neapolitan_chord("C", octave=3, duration=4.0))  # bII — the star
strings.add(Chord("G", "dom7", 3, duration=4.0))
strings.add(Chord("C", "min", 3, duration=4.0))
strings.add(Chord("F", "min", 3, duration=4.0))
strings.extend(augmented_sixth("C", "german", octave=3, duration=4.0))
strings.extend(picardy_third("C", octave=3, duration=4.0))  # major ending

# Melody — expressive over the chromatic harmony
lead = song.add_track(Track(name="lead", instrument="piano", volume=0.55, pan=0.15))
lead.extend(scale("C", "minor", octave=5, length=4))
lead.extend(scale("Ab", "major", octave=5, length=4))
lead.extend([Note("F", 5, 2.0), Note("Eb", 5, 2.0)])  # over Neapolitan
lead.extend([Note("D", 5, 1.0), Note("B", 4, 1.0), Note("C", 5, 2.0)])
lead.add(Note("C", 5, 2.0))
lead.add(Note("Eb", 5, 2.0))
lead.extend([Note("Ab", 4, 1.0), Note("F#", 4, 1.0), Note("G", 4, 2.0)])
lead.add(Note("E", 5, 2.0))  # Picardy — major 3rd as final note
lead.add(Note("C", 5, 2.0))

song.effects = {
    "strings": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
    "lead": EffectsChain().add(delay, delay_ms=375, feedback=0.25, wet=0.2),
}
