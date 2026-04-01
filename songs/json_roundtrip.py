"""json_roundtrip.py — Showcases Song.export_json/load_json round-trip.

This song exports itself to JSON, reloads it, and uses the reloaded
version as proof that serialization works. The actual music is a simple
ambient piece that makes a nice test case.

Style: Ambient, Fm, 80 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, stereo_width

song = Song(title="JSON Roundtrip", bpm=80)

r = Note.rest

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35))
for _ in range(8):
    pad.extend(
        [
            Chord("F", "min7", 3, duration=4.0),
            Chord("Db", "maj7", 3, duration=4.0),
        ]
    )

lead = song.add_track(Track(name="lead", instrument="triangle", volume=0.4, pan=0.2))
melody = [
    Note("F", 5, 1.0),
    Note("Ab", 5, 0.5),
    Note("C", 6, 0.5),
    Note("Bb", 5, 1.0),
    Note("Ab", 5, 1.0),
    Note("F", 5, 2.0),
    r(2.0),
]
for _ in range(8):
    lead.extend(melody)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for _ in range(8):
    bass.extend([Note("F", 2, 4.0), Note("Db", 2, 4.0)])

song.effects = {
    "pad": EffectsChain()
    .add(reverb, room_size=0.8, wet=0.4, label="reverb")
    .add(stereo_width, width=1.6, label="stereo_width"),
    "lead": EffectsChain().add(reverb, room_size=0.5, wet=0.2, label="reverb"),
}
