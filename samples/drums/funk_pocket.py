"""Funk pocket - Clyde Stubblefield ghost note groove with tight 16ths."""

from code_music import (
    Note,
    Chord,
    Track,
    Song,
    EffectsChain,
    compress,
    distortion,
    F,
    MF,
    MP,
)
from code_music.theory.rhythm import funk_drum_pattern, apply_groove, groove_template

song = Song(title="Funk Pocket", bpm=98, key_sig="E", time_sig=(4, 4))

# Funk drums with ghost notes
drums = funk_drum_pattern(bars=4, ghost_velocity=0.25, seed=42)

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
kick.extend(drums["kick"])

snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.7))
snare.extend(drums["snare"])

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.4))
hat.extend(drums["hat"])

# Funk bass: E7#9 one-chord vamp
bass = song.add_track(Track(name="bass", instrument="moog_bass", volume=0.65, pan=0.05))
funk_groove = groove_template("funk_tight")
# Syncopated 16th note bass
bass_pattern = [
    Note("E", 2, 0.25, F),
    Note.rest(0.25),
    Note("E", 2, 0.25, MF),
    Note("G", 2, 0.25, MP),
    Note("E", 2, 0.5, F),
    Note.rest(0.25),
    Note("E", 3, 0.25, MF),
    Note("E", 2, 0.25, F),
    Note.rest(0.25),
    Note("G", 2, 0.25, MP),
    Note("A", 2, 0.25, MF),
    Note("E", 2, 0.5, F),
    Note.rest(0.25),
    Note("D", 2, 0.25, MP),
]
bass.extend(apply_groove(bass_pattern * 4, funk_groove, strength=0.6))

# Clavinet: scratchy 16th-note chops
clav = song.add_track(Track(name="clav", instrument="harpsichord", volume=0.4, pan=-0.2))
clav_chop = [
    Chord("E", "dom7#9", 4, duration=0.25, velocity=MF),
    Note.rest(0.25),
    Chord("E", "dom7#9", 4, duration=0.25, velocity=0.3),
    Note.rest(0.25),
] * 16
clav.extend(clav_chop)

song.effects = {
    "bass": EffectsChain()
    .add(compress, threshold=0.4, ratio=6.0)
    .add(distortion, drive=1.5, wet=0.2),
    "clav": EffectsChain().add(distortion, drive=2.0, tone=0.7, wet=0.3),
}
