"""Quartal Towers — McCoy Tyner stacked-4ths voicings over a modal vamp."""

from code_music import EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import quartal_voicing

song = Song(title="Quartal Towers", bpm=140)

# Quartal voicings cycling through modes
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.5, pan=0.1))
for root in ["D", "G", "C", "F", "Bb", "Eb", "Ab", "D"]:
    piano.extend(quartal_voicing(root, octave=3, duration=4.0, layers=4))

# Bass pedal
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for _ in range(8):
    bass.extend([Note("D", 2, 2.0), Note("A", 2, 2.0)])

# Drums
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.55))
for _ in range(32):
    kick.add(Note("C", 2, 1.0))

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.2, pan=0.15))
for _ in range(64):
    hat.add(Note("C", 5, 0.5))

song.effects = {
    "piano": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
    "bass": EffectsChain().add(delay, delay_ms=200, feedback=0.1, wet=0.1),
}
