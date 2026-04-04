"""Metric Shift — metric modulation from 120 BPM to 160 BPM via subdivision reinterpretation."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, euclid, reverb
from code_music.theory import metric_modulation

# Start at 120, modulate to 160 (16ths → triplets: 120 * 4/3 = 160)
bpm_start = 120
bpm_after = metric_modulation(bpm_start, old_subdivision=4, new_subdivision=3)

song = Song(title="Metric Shift", bpm=bpm_start)

# Section 1: straight 16ths at 120 BPM
drums = song.add_track(Track(name="drums", instrument="drums_kick", volume=0.6))
drums.extend(euclid(4, 16, "C", 2, 0.25))
drums.extend(euclid(4, 16, "C", 2, 0.25))

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35))
hat.extend([Note("C", 5, 0.25) for _ in range(32)])

chords = song.add_track(Track(name="chords", instrument="organ", volume=0.4, pan=-0.1))
chords.add(Chord("A", "min7", 3, duration=4.0))
chords.add(Chord("D", "min7", 3, duration=4.0))

# Section 2: reinterpret at new BPM via bpm_ramp
# The mathematical pivot: what was a 16th note becomes a triplet beat
lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15))
lead.extend([Note("A", 5, 0.5), Note("C", 6, 0.5), Note("E", 5, 0.5), Note("G", 5, 0.5)])
lead.extend([Note("D", 5, 0.5), Note("F", 5, 0.5), Note("A", 5, 0.5), Note("C", 6, 0.5)])
# Triplet feel section
triplet_dur = 1.0 / 3
for _ in range(4):
    lead.extend([Note("A", 5, triplet_dur), Note("C", 6, triplet_dur), Note("E", 6, triplet_dur)])

song.effects = {
    "lead": EffectsChain().add(delay, delay_ms=250, feedback=0.2, wet=0.15),
    "chords": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
}
