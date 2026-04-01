"""split_personality.py — Showcases Track.split() for surgical track editing.

A single long melody track is split at bar 8, then the two halves get
different effects and are recombined with a transpose on the second half.

Style: Electronica, Am, 118 BPM.
"""

from code_music import EffectsChain, Note, Song, Track, delay, reverb

song = Song(title="Split Personality", bpm=118)

r = Note.rest

# Build one long melody
full_melody = Track(name="melody", instrument="sawtooth", volume=0.5)
phrase = [
    Note("A", 4, 0.5),
    Note("C", 5, 0.5),
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 1.0),
    Note("A", 4, 1.0),
]
for _ in range(16):
    full_melody.extend(phrase)

# Split at bar 8 (beat 32)
first_half, second_half = full_melody.split(at_beat=32.0)

# Transpose the second half up a fourth and fade it out
second_half_up = second_half.transpose(5).fade_out(beats=16.0)

# Recombine: first half with fade in, then transposed second half
song.add_track(first_half.fade_in(beats=8.0).concat(second_half_up))

# Bass follows the same split-and-shift structure
bass_full = Track(name="bass", instrument="bass", volume=0.6)
for _ in range(16):
    bass_full.extend([Note("A", 2, 2.0), Note("E", 2, 2.0)])

bass_a, bass_b = bass_full.split(at_beat=32.0)
song.add_track(bass_a.concat(bass_b.transpose(5)))

# Drums straight through
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.75))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.5))
for _ in range(16):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)])

song.effects = {
    "melody": EffectsChain()
    .add(delay, delay_ms=254, feedback=0.25, wet=0.18)
    .add(reverb, room_size=0.45, wet=0.15),
}
