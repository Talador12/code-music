"""Guitar Techniques — hammer-ons, pull-offs, and slides."""

from code_music import EffectsChain, Note, Song, Track, delay
from code_music.theory import hammer_on, pull_off, slide

song = Song(title="Guitar Techniques", bpm=100)

lead = song.add_track(Track(name="lead", instrument="pluck", volume=0.5, pan=0.15))

# Hammer-on: E to G
lead.extend(hammer_on(Note("E", 4, 0.5), Note("G", 4, 0.5)))

# Pull-off: G back to E
lead.extend(pull_off(Note("G", 4, 0.5), Note("E", 4, 0.5)))

# Slide from C to G
lead.extend(slide(Note("C", 4, 1.0), Note("G", 4, 1.0), steps=4))

# Another round
lead.extend(hammer_on(Note("A", 4, 0.5), Note("C", 5, 0.5)))
lead.extend(slide(Note("C", 5, 1.0), Note("E", 5, 1.0), steps=3))
lead.extend(pull_off(Note("E", 5, 0.5), Note("D", 5, 0.5)))

song.effects = {
    "lead": EffectsChain().add(delay, delay_ms=300, feedback=0.2, wet=0.15),
}
