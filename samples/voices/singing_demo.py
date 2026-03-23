"""Singing demo: macOS voices doing their best to sing.

Tests every musically interesting say voice back-to-back.
Bells, Bubbles, Organ, Cellos, Boing, Wobble — the full zoo.

Run: code-music samples/voices/singing_demo.py -o /tmp/singing.wav
"""

from code_music import Song, VoiceClip, VoiceTrack

song = Song(title="singing_demo", bpm=90)

vox = song.add_voice_track(VoiceTrack(name="voices"))

demos = [
    # (text, voice, rate, beat_offset, pan)
    ("la la la la la", "Cellos", 90, 0.0, 0.0),
    ("aaaah ooooh eeeee", "Organ", 80, 3.0, -0.3),
    ("boing boing boing", "Boing", 100, 6.0, 0.3),
    ("ding ding ding ding", "Bells", 110, 9.0, -0.3),
    ("bubble bubble bubble", "Bubbles", 100, 12.0, 0.3),
    ("wobble wobble wobble", "Wobble", 90, 15.0, -0.2),
    ("zar vox singing now", "Zarvox", 85, 18.0, 0.0),
    ("tri noid choir voice", "Trinoids", 80, 21.0, 0.2),
    ("deep cello sound aaah", "Cellos", 70, 24.0, 0.0),
    ("good news everybody", "Good News", 100, 27.0, -0.3),
    ("bad news everybody", "Bad News", 100, 30.0, 0.3),
]

for text, voice, rate, beat, pan_v in demos:
    vox.add(
        VoiceClip(text, voice=voice, rate=rate, pan=pan_v, volume=0.8),
        beat_offset=beat,
    )
