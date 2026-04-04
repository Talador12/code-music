"""Palm Mute Riff — chunky metal rhythm with palm-muted power chords."""

from code_music import EffectsChain, Note, Song, Track, distortion, reverb
from code_music.theory import dotted, palm_mute, split_note

song = Song(title="Palm Mute Riff", bpm=140)

# Power chord riff
riff = [
    Note("E", 3, 1.0),
    Note("E", 3, 0.5),
    Note("G", 3, 0.5),
    Note("A", 3, 1.0),
    Note("E", 3, 1.0),
]

# Palm mute the whole riff
muted = palm_mute(riff, decay_factor=0.25)

rhythm = song.add_track(Track(name="rhythm", instrument="sawtooth", volume=0.5, pan=-0.15))
for _ in range(4):
    rhythm.extend(muted)

# Add a dotted note accent
accent = dotted(Note("B", 3, 1.0))
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=0.15))
lead.add(accent)
# Split a whole note into rapid 16ths
rapid = split_note(Note("E", 4, 2.0), 8)
lead.extend(rapid)

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.6))
for _ in range(16):
    kick.add(Note("C", 2, 0.5))
    kick.add(Note.rest(0.5))

song.effects = {
    "rhythm": EffectsChain().add(distortion, gain=4.0, wet=0.6),
    "lead": EffectsChain().add(distortion, gain=3.0, wet=0.5),
}
