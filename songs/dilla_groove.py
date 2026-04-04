"""Dilla Groove — J Dilla timing feel applied to a straight beat."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import apply_groove, groove_template

song = Song(title="Dilla Groove", bpm=86)

# Straight 16th note pattern
straight = [Note("C", 4, 0.25) for _ in range(64)]

# Apply J Dilla groove
dilla = groove_template("j_dilla")
grooved = apply_groove(straight, dilla, strength=0.8)

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.6))
kick.extend(grooved)

# Hi-hat with MPC swing
hat_straight = [Note("C", 5, 0.25) for _ in range(64)]
hat_grooved = apply_groove(hat_straight, groove_template("mpc_swing"))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.25, pan=0.15))
hat.extend(hat_grooved)

# Chord pad
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35, pan=-0.1))
pad.add(Chord("D", "min9", 3, duration=16.0))

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for _ in range(8):
    bass.extend([Note("D", 2, 1.0), Note("F", 2, 0.5), Note("A", 2, 0.5)])

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
}
