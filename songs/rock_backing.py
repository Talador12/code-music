"""Rock Backing — auto-generated backing track for practice."""

from code_music import EffectsChain, Song, Track, distortion, reverb
from code_music.theory import backing_track

song = Song(title="Rock Backing", bpm=130)

prog = [("A", "min"), ("F", "maj"), ("C", "maj"), ("G", "maj")] * 2
parts = backing_track(prog, key="A", style="rock")

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
bass.extend(parts["bass"])

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.6))
kick.extend(parts["kick"])

snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.5))
snare.extend(parts["snare"])

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.25, pan=0.15))
hat.extend(parts["hat"])

song.effects = {
    "bass": EffectsChain().add(distortion, gain=1.5, wet=0.15),
    "snare": EffectsChain().add(reverb, room_size=0.3, wet=0.15),
}
