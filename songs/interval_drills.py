"""Interval Drills — ear training exercises rendered as a playable song."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import ear_training_intervals

song = Song(title="Interval Drills", bpm=60)

exercises = ear_training_intervals(count=12, max_semitones=12, seed=42)

melody = song.add_track(Track(name="melody", instrument="piano", volume=0.5, pan=0.0))
for ex in exercises:
    melody.add(ex["note_a"])
    melody.add(ex["note_b"])
    melody.add(Note.rest(1.0))  # pause between exercises

song.effects = {
    "melody": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
}
