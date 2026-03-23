"""Spoken word over a beat: Whisper voice poetry over lo-fi hip-hop.

Inspired by spoken word artists + beatpoetry + lo-fi. The Whisper macOS
voice has a genuinely intimate quality that works over slow beats.

Run: code-music samples/voices/spoken_word_beat.py -o /tmp/spoken_beat.wav
"""

from code_music import Chord, Note, Song, Track, VoiceClip, VoiceTrack, reverb

song = Song(title="spoken_word_beat", bpm=75)

# ── Lo-fi beat ─────────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.85))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.4))
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35, pan=-0.2))
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))

r = Note.rest
for _ in range(8):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    hat.extend([Note("F", 5, 0.5)] * 8)
    pad.add(Chord("A", "min7", 3, duration=4.0, velocity=0.5))
    bass.extend([Note("A", 2, 1.0), r(1.0), Note("G", 2, 1.0), r(1.0)])

# ── Spoken word ────────────────────────────────────────────────────────────
vox = song.add_voice_track(VoiceTrack(name="spoken"))
lines = [
    ("code is music written in silence", "Whisper", 95, 0.0),
    ("every function a phrase", "Whisper", 90, 3.5),
    ("every loop a rhythm", "Whisper", 90, 6.5),
    ("variables hold the notes", "Whisper", 85, 9.5),
    ("until the compiler sets them free", "Whisper", 80, 13.0),
    ("and the output", "Whisper", 90, 17.5),
    ("is the song we always meant to write", "Whisper", 80, 19.5),
]
for text, voice, rate, beat in lines:
    vox.add(VoiceClip(text, voice=voice, rate=rate, pan=0.0, volume=0.75), beat_offset=beat)

song._effects = {
    "pad": lambda s, sr: reverb(s, sr, room_size=0.65, wet=0.3),
}
