"""shoegaze_haze.py — Shoegaze. F#m, 86 BPM. My Bloody Valentine wall of sound.

Drenched-in-reverb guitar layers, barely-there drums, and a melody that
swims through the distortion. Uses Track.merge to layer two guitar textures.

Style: Shoegaze, F#m, 86 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, distortion, reverb, stereo_width

song = Song(title="Shoegaze Haze", bpm=86)

r = Note.rest

# Two guitar layers merged into one massive wall
guitar_a = Track(name="guitar", instrument="sawtooth", volume=0.4, pan=-0.3)
guitar_b = Track(name="guitar", instrument="sawtooth", volume=0.4, pan=-0.3)
for _ in range(12):
    guitar_a.extend(
        [
            Chord("F#", "min", 3, duration=4.0),
            Chord("D", "maj", 3, duration=4.0),
        ]
    )
    guitar_b.extend(
        [
            r(2.0),
            Chord("F#", "min", 4, duration=2.0),
            r(2.0),
            Chord("D", "maj", 4, duration=2.0),
        ]
    )
song.add_track(guitar_a.merge(guitar_b))

# Barely there drums
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.45))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.15))
for _ in range(12):
    kick.extend([Note("C", 2, 2.0), r(2.0), Note("C", 2, 2.0), r(2.0)])
    hat.extend([Note("F#", 6, 0.5)] * 16)

# Bass — simple root notes under the wash
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for _ in range(12):
    bass.extend([Note("F#", 2, 4.0), Note("D", 2, 4.0)])

# Melody — barely audible, floating
lead = song.add_track(Track(name="lead", instrument="triangle", volume=0.3, pan=0.2))
for _ in range(6):
    lead.extend(
        [
            Note("A", 5, 1.0),
            Note("F#", 5, 0.5),
            Note("E", 5, 0.5),
            Note("D", 5, 1.0),
            Note("C#", 5, 1.0),
            Note("F#", 5, 2.0),
            r(2.0),
            Note("A", 5, 0.5),
            Note("B", 5, 0.5),
            Note("A", 5, 1.0),
            Note("F#", 5, 1.0),
            r(5.0),
        ]
    )

song.effects = {
    "guitar": EffectsChain()
    .add(distortion, drive=2.0, tone=0.3, wet=0.4)
    .add(reverb, room_size=0.9, wet=0.55)
    .add(stereo_width, width=2.0),
    "lead": EffectsChain().add(reverb, room_size=0.85, wet=0.5),
    "kick": EffectsChain().add(reverb, room_size=0.6, wet=0.2),
}
