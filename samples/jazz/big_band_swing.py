"""Big band swing - Count Basie meets Thad Jones. Brass hits and walking bass."""

from code_music import (
    Note,
    Chord,
    Track,
    Song,
    EffectsChain,
    scale,
    reverb,
    compress,
    F,
    FF,
    MF,
    MP,
    P,
    dynamics,
    octave_down,
)
from code_music.symphony import orchestrate_big_band
from code_music.theory.rhythm import big_band_drum_pattern, apply_groove, groove_template

song = Song(title="Big Band Swing", bpm=160, key_sig="Bb", time_sig=(4, 4))

# Melody: bluesy swing head
head = [
    Note("Bb", 5, 1.0, F),
    Note("D", 6, 0.5, MF),
    Note("F", 5, 0.5, MF),
    Note("Bb", 5, 1.0, F),
    Note.rest(0.5),
    Note("Ab", 5, 0.5, MF),
    Note("G", 5, 1.0, F),
    Note("F", 5, 0.5, MF),
    Note("Eb", 5, 0.5, MP),
    Note("D", 5, 2.0, F),
    Note.rest(1.0),
    Note("Eb", 5, 0.5, MF),
    Note("F", 5, 0.5, MF),
    Note("G", 5, 1.0, F),
    Note("Ab", 5, 0.5, MF),
    Note("Bb", 5, 1.5, FF),
    Note.rest(1.0),
]

# Use the big band orchestrator
progression = [("Bb", "maj7"), ("Eb", "dom7"), ("Bb", "maj7"), ("F", "dom7")]
mvt = orchestrate_big_band(head * 2, progression=progression, key="Bb", style="swing", seed=42)

# Convert to song tracks
for part in mvt.parts.values():
    song.add_track(part.to_track())

# Override drums with proper big band pattern
drums = big_band_drum_pattern(bars=len(head) * 2 // 4 + 1, feel="swing")
ride = song.add_track(Track(name="ride_cymbal", instrument="drums_ride", volume=0.4))
ride.extend(drums["ride"])
hat_foot = song.add_track(Track(name="hat_foot", instrument="drums_hat", volume=0.25))
hat_foot.extend(drums["hat_foot"])

# Apply big band groove
bb_groove = groove_template("big_band")

song.effects = {
    "trumpet_1": EffectsChain().add(reverb, room_size=0.4, wet=0.15),
    "piano": EffectsChain().add(compress, threshold=0.5, ratio=3.0),
}
