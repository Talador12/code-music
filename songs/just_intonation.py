"""Just Intonation — a C major triad with cent offsets for pure tuning."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import detune_to_just

song = Song(title="Just Intonation", bpm=60)

# C major triad — E and G need detuning for just intonation
notes = [Note("C", 4, 4.0), Note("E", 4, 4.0), Note("G", 4, 4.0), Note("C", 5, 4.0)]
offsets = detune_to_just(notes, key="C")

# Play the notes (offsets are metadata — would be applied in a DAW)
lead = song.add_track(Track(name="lead", instrument="organ", volume=0.5))
lead.extend(notes)

song.effects = {"lead": EffectsChain().add(reverb, room_size=0.6, wet=0.3)}
