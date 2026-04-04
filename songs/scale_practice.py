"""Scale Practice — ascending and descending through all modes."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import scale_exercise

song = Song(title="Scale Practice", bpm=100)

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.0))

# Run through major, minor, dorian, mixolydian
for mode in ["major", "minor", "dorian", "mixolydian"]:
    notes = scale_exercise("C", mode, "both", octave=4, duration=0.25)
    lead.extend(notes)
    lead.add(Note.rest(1.0))  # pause between scales

song.effects = {
    "lead": EffectsChain().add(reverb, room_size=0.3, wet=0.15),
}
