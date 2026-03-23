"""Daft Punk vocoder vibes: Cellos + Organ voices, robotic and funky.

Daft Punk used a Talk Box / vocoder on "Around the World", "Harder Better
Faster Stronger" etc. We approximate with macOS Cellos + Organ voices,
some pitch shifting, and reverb. No copyright issues — original text/melody.

Run: code-music samples/voices/daft_punk_vocoder.py -o /tmp/daft_vocoder.wav
"""

from code_music import Chord, Note, Song, Track, VoiceClip, VoiceTrack, delay, reverb

song = Song(title="daft_punk_vocoder", bpm=123)

# ── Funk rhythm section ────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.95))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.5))
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.8))
stab = song.add_track(Track(name="stab", instrument="stab", volume=0.6, pan=0.2))

r = Note.rest
k = Note("C", 2, 1.0)
h = Note("F", 5, 0.5)
for _ in range(4):
    kick.extend([k, r(1.0), k, r(1.0)])
    hat.extend([h, h, h, h, h, h, h, h])
    bass.extend(
        [
            Note("E", 2, 0.5),
            Note("E", 2, 0.25),
            r(0.25),
            Note("G", 2, 0.5),
            r(0.5),
            Note("A", 2, 0.25),
            Note("E", 2, 0.25),
            r(0.5),
            Note("G", 2, 0.5),
            r(0.5),
        ]
    )
    stab.extend([r(1.0), Chord("E", "min7", 3, duration=0.5), r(2.5)])

# ── Vocoder voice layer ────────────────────────────────────────────────────
vox = song.add_voice_track(VoiceTrack(name="vocoder"))
phrases = [
    ("work it harder make it better", "Cellos", 110, 0.0, 0.0),
    ("do it faster makes us stronger", "Cellos", 110, 4.0, 0.0),
    ("more than ever hour after", "Organ", 100, 8.0, 0.3),
    ("our work is never over", "Organ", 100, 12.0, -0.3),
]
for text, voice, rate, beat, pan_v in phrases:
    vox.add(VoiceClip(text, voice=voice, rate=rate, pan=pan_v, volume=0.8), beat_offset=beat)

song._effects = {
    "stab": lambda s, sr: reverb(s, sr, room_size=0.3, wet=0.15),
    "vocoder": lambda s, sr: delay(s, sr, delay_ms=250.0, feedback=0.3, wet=0.2, ping_pong=True),
}
