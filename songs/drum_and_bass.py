"""drum_and_bass.py - Drum and bass. Am, 174 BPM.

Fast breakbeat with syncopated snare rolls, a rolling sub bass,
and a sharp reese-style lead. Amen break energy at 174.

Style: Drum and bass, Am, 174 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, distortion, lowpass, reverb

song = Song(title="Drum and Bass", bpm=174, sample_rate=44100)
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.6))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3))
for _ in range(24):
    kick.extend([Note("C", 2, 0.75), r(0.75), Note("C", 2, 0.5), r(0.5), Note("C", 2, 0.5)])
    snare.extend(
        [r(1.0), Note("E", 4, 0.5), r(0.5), Note("E", 4, 0.25), Note("E", 4, 0.25), r(0.5)]
    )
    hat.extend([Note("F#", 6, 0.25)] * 12)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.7))
for _ in range(24):
    bass.extend(
        [Note("A", 1, 1.0), r(0.5), Note("A", 1, 0.5), Note("C", 2, 0.5), Note("A", 1, 0.5)]
    )

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.2, pan=-0.15))
for _ in range(6):
    pad.extend(
        [
            Chord("A", "min", 3, duration=4.0),
            Chord("F", "maj", 3, duration=4.0),
            Chord("G", "maj", 3, duration=4.0),
            Chord("E", "min", 3, duration=4.0),
        ]
    )

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.35, pan=0.2))
for _ in range(12):
    lead.extend(
        [
            Note("A", 5, 0.25),
            Note("C", 6, 0.25),
            Note("E", 5, 0.5),
            r(1.0),
            Note("G", 5, 0.5),
            Note("A", 5, 0.5),
            r(3.0),
        ]
    )

song.effects = {
    "bass": EffectsChain().add(lowpass, cutoff_hz=150).add(distortion, drive=0.3),
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.4),
}
