"""hawaiian_slack_key.py — Hawaiian slack-key guitar. G major, 80 BPM.

Open tuning fingerpicking over a gentle ukulele-style groove.
Uses Track.loop for the repeating picking pattern.

Style: Hawaiian slack-key, G major, 80 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb

song = Song(title="Hawaiian Slack Key", bpm=80)

r = Note.rest

# Slack-key guitar picking pattern — one bar, looped
pick_bar = Track(name="guitar", instrument="pluck", volume=0.55, pan=0.1)
pick_bar.extend(
    [
        Note("G", 3, 0.5),
        Note("B", 3, 0.5),
        Note("D", 4, 0.5),
        Note("G", 4, 0.5),
        Note("B", 4, 0.5),
        Note("G", 4, 0.5),
        Note("D", 4, 0.5),
        Note("B", 3, 0.5),
    ]
)
song.add_track(pick_bar.loop(16))

# Bass — gentle root movement
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.45))
for _ in range(8):
    bass.extend([Note("G", 2, 4.0), Note("C", 2, 4.0)])

# Ukulele strum
uke = song.add_track(Track(name="uke", instrument="pluck", volume=0.3, pan=-0.2))
for _ in range(8):
    uke.extend(
        [
            Chord("G", "maj", 4, duration=2.0),
            Chord("G", "maj", 4, duration=1.0),
            r(1.0),
            Chord("C", "maj", 4, duration=2.0),
            Chord("C", "maj", 4, duration=1.0),
            r(1.0),
        ]
    )

# Melody — pentatonic
lead = song.add_track(Track(name="lead", instrument="triangle", volume=0.4, pan=0.15))
for _ in range(4):
    lead.extend(
        [
            Note("G", 5, 1.0),
            Note("A", 5, 0.5),
            Note("B", 5, 0.5),
            Note("D", 6, 1.0),
            Note("B", 5, 1.0),
            Note("A", 5, 0.5),
            Note("G", 5, 0.5),
            Note("E", 5, 1.0),
            Note("G", 5, 2.0),
            r(6.0),
        ]
    )

song.effects = {
    "guitar": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
    "lead": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
}
