"""Robot choir: Zarvox + Trinoids + Cellos singing "ah" syllables in Cm.

Uses macOS say voices. Zarvox = alien robot, Trinoids = eerie mechanical,
Cellos = deep resonant vocal cello. Together they make a genuinely weird
synthetic choir.

Run: code-music samples/voices/robot_choir.py -o /tmp/robot_choir.wav
"""

from code_music import Note, Song, Track, VoiceClip, VoiceTrack, reverb

song = Song(title="robot_choir", bpm=72)

# ── Instrument pad underneath ──────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=0.0))
for _ in range(4):
    pad.add(Note("C", 3, duration=4.0, velocity=0.5))

# ── Voice tracks ───────────────────────────────────────────────────────────
# Zarvox on root (C)
vox1 = song.add_voice_track(VoiceTrack(name="zarvox"))
vox1.add(VoiceClip("aaaah", voice="Zarvox", rate=80, pan=-0.4, volume=0.7), beat_offset=0.0)
vox1.add(VoiceClip("ooooh", voice="Zarvox", rate=80, pan=-0.4, volume=0.7), beat_offset=4.0)
vox1.add(
    VoiceClip("eeee aaah oooh", voice="Zarvox", rate=70, pan=-0.4, volume=0.7), beat_offset=8.0
)
vox1.add(VoiceClip("aaaaah", voice="Zarvox", rate=75, pan=-0.4, volume=0.75), beat_offset=12.0)

# Trinoids on fifth (G)
vox2 = song.add_voice_track(VoiceTrack(name="trinoids"))
vox2.add(VoiceClip("aaaah", voice="Trinoids", rate=85, pan=0.4, volume=0.65), beat_offset=0.5)
vox2.add(VoiceClip("ooooh", voice="Trinoids", rate=85, pan=0.4, volume=0.65), beat_offset=4.5)
vox2.add(
    VoiceClip("eeee oooh aaah", voice="Trinoids", rate=75, pan=0.4, volume=0.65), beat_offset=8.5
)
vox2.add(VoiceClip("ooooooh", voice="Trinoids", rate=80, pan=0.4, volume=0.65), beat_offset=12.5)

# Cellos as bass voice
vox3 = song.add_voice_track(VoiceTrack(name="cellos"))
vox3.add(VoiceClip("aaah oooh aaah", voice="Cellos", rate=70, pan=0.0, volume=0.7), beat_offset=0.0)
vox3.add(VoiceClip("deep deep aaah", voice="Cellos", rate=65, pan=0.0, volume=0.7), beat_offset=8.0)

# Whisper for texture
vox4 = song.add_voice_track(VoiceTrack(name="whisper"))
vox4.add(
    VoiceClip("voices in the machine", voice="Whisper", rate=90, pan=-0.2, volume=0.5),
    beat_offset=6.0,
)
vox4.add(
    VoiceClip("singing in the code", voice="Whisper", rate=90, pan=0.2, volume=0.5),
    beat_offset=12.0,
)

song.effects = {
    "pad": lambda s, sr: reverb(s, sr, room_size=0.8, wet=0.4),
}
