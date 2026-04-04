"""Song 300 — the 300th song milestone, celebrating with every trick in the book."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import (
    andalusian_cadence,
    apply_groove,
    augment,
    generate_scale_melody,
    groove_template,
    progression_from_roman,
    reharmonize,
    target_chord_tones,
)

song = Song(title="Song 300", bpm=108)

# Original pop progression, then jazzed up
original = progression_from_roman(["I", "V", "vi", "IV"], "C")
jazz = reharmonize(original, key="C", style="jazz")

# Pad with the jazz reharmonization
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35, pan=-0.15))
for root, shape in jazz:
    pad.add(Chord(root, shape, 3, duration=4.0))
# Andalusian cadence ending
for root, shape in andalusian_cadence("A"):
    pad.add(Chord(root, shape, 3, duration=4.0))

# Generated melody with arch contour
lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15))
melody = generate_scale_melody("C", "major", length=24, octave=5, contour="arch", seed=300)
lead.extend(melody)

# Chord tone targeting for the jazz section
targeting = target_chord_tones(jazz, key="C", notes_per_chord=4, seed=300)
lead.extend(targeting)

# Augmented motif as ending
motif = [Note("C", 5, 0.5), Note("E", 5, 0.5), Note("G", 5, 0.5)]
lead.extend(augment(motif, factor=3.0))

# Grooved drums
kick_straight = [Note("C", 2, 0.25) for _ in range(64)]
kick_grooved = apply_groove(kick_straight, groove_template("motown"))
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.55))
kick.extend(kick_grooved)

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root, _ in jazz:
    bass.add(Note(root, 2, 4.0))
for root, _ in andalusian_cadence("A"):
    bass.add(Note(root, 2, 4.0))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
    "lead": EffectsChain().add(delay, delay_ms=300, feedback=0.2, wet=0.15),
}
