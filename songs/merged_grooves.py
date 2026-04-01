"""merged_grooves.py — Showcases Track.merge() for layering patterns.

Two hi-hat patterns (ride + offbeat) are merged into one stereo track.
A call-and-response melody merges rests with fills from a second voice.

Style: Neo-soul, Em, 92 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb

song = Song(title="Merged Grooves", bpm=92)

r = Note.rest

# ── Drums — merge two hat patterns into one ──────────────────────────────
ride = Track(name="hats", instrument="drums_hat", volume=0.35, pan=0.2)
offbeat = Track(name="hats", instrument="drums_hat", volume=0.35, pan=0.2)
for _ in range(16):
    ride.extend([Note("F#", 6, 1.0), r(1.0), Note("F#", 6, 1.0), r(1.0)])
    offbeat.extend(
        [
            r(0.5),
            Note("F#", 6, 0.5, velocity=0.4),
            r(0.5),
            Note("F#", 6, 0.5, velocity=0.4),
            r(0.5),
            Note("F#", 6, 0.5, velocity=0.4),
            r(0.5),
            Note("F#", 6, 0.5, velocity=0.4),
        ]
    )
song.add_track(ride.merge(offbeat))

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.75))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.5))
for _ in range(16):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 0.5), r(0.5), Note("C", 2, 1.0)])
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)])

# ── Melody — merge call with response fills ──────────────────────────────
call = Track(name="keys", instrument="piano", volume=0.5, pan=-0.15)
response = Track(name="keys", instrument="piano", volume=0.5, pan=-0.15)
for _ in range(8):
    call.extend([Note("E", 5, 0.5), Note("G", 5, 0.5), Note("B", 5, 1.0), r(2.0), r(4.0)])
    response.extend([r(4.0), Note("D", 5, 0.5), Note("E", 5, 0.5), Note("G", 5, 1.0), r(2.0)])
song.add_track(call.merge(response))

# ── Bass ─────────────────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
for _ in range(16):
    bass.extend([Note("E", 2, 2.0), Note("G", 2, 1.0), Note("B", 2, 1.0)])

# ── Pad ──────────────────────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.25))
for _ in range(8):
    pad.extend([Chord("E", "min7", 3, duration=4.0), Chord("A", "min7", 3, duration=4.0)])

song.effects = {
    "keys": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
}
