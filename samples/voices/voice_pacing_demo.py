"""Voice pacing demo: narration vs rap timing side-by-side.

Showcases VoiceClip convenience constructors:
- VoiceClip.narration(...)  -> calmer pacing, longer pauses
- VoiceClip.rap(...)        -> faster pacing, tighter pauses

Run: code-music samples/voices/voice_pacing_demo.py -o /tmp/voice_pacing_demo.wav
"""

from code_music import Note, Song, Track, VoiceClip, VoiceTrack

song = Song(title="voice_pacing_demo", bpm=96)

# Simple pulse so pacing differences are easier to hear.
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.5))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.25))
for _ in range(12):
    kick.extend([Note("C", 2, 1.0), Note.rest(1.0), Note("C", 2, 1.0), Note.rest(1.0)])
    hat.extend([Note("F", 5, 0.5)] * 8)

vox = song.add_voice_track(VoiceTrack(name="voice_pacing"))

line = "code becomes rhythm, and rhythm becomes code."

vox.add(
    VoiceClip.narration(line, voice="Samantha", backend="say", volume=0.78, pan=-0.25),
    beat_offset=0.0,
)

vox.add(
    VoiceClip.rap(line, voice="Zarvox", backend="say", volume=0.75, pan=0.25),
    beat_offset=8.0,
)
