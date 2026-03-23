"""Operatic drama: Samantha + Cellos doing operatic phrases over strings.

Full theatrical treatment: strings swell, then voice enters. The Cellos
voice at slow rate has a genuinely eerie soprano-ish quality.

Run: code-music samples/voices/operatic_drama.py -o /tmp/opera.wav
"""

from code_music import Chord, Note, Song, Track, VoiceClip, VoiceTrack, reverb

song = Song(title="operatic_drama", bpm=64)

# ── Orchestral strings swell ───────────────────────────────────────────────
for inst, pan_v, vol in [("strings", -0.3, 0.5), ("cello", 0.3, 0.55)]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=vol, pan=pan_v))
    for ch, sh in [("D", "min7"), ("A#", "maj7"), ("F", "maj7"), ("C", "dom7")] * 2:
        tr.add(Chord(ch, sh, 3, duration=4.0, velocity=0.6))

# ── Harp punctuation ───────────────────────────────────────────────────────
harp = song.add_track(Track(name="harp", instrument="harp", volume=0.45))
harp.extend(
    [
        Note.rest(4.0),
        Note("F", 5, 0.5),
        Note("A", 5, 0.5),
        Note("D", 6, 1.0),
        Note.rest(2.0),
        Note("C", 6, 0.5),
        Note("A", 5, 0.5),
        Note.rest(24.0),
    ]
)

# ── Operatic voice ─────────────────────────────────────────────────────────
soprano = song.add_voice_track(VoiceTrack(name="soprano"))
arias = [
    ("aaaaaah", "Cellos", 65, 4.0, 0.0, 0.8),
    ("oh fortuna", "Cellos", 70, 8.0, -0.1, 0.8),
    ("aaaaaah ooooh eeeeeh", "Cellos", 60, 12.0, 0.1, 0.85),
    ("in this silent night", "Samantha", 75, 16.0, 0.0, 0.7),
    ("the music calls to me", "Samantha", 72, 20.0, 0.0, 0.7),
    ("aaaaah oooooh", "Cellos", 60, 24.0, 0.0, 0.85),
]
for text, voice, rate, beat, pan_v, vol in arias:
    soprano.add(
        VoiceClip(text, voice=voice, rate=rate, pan=pan_v, volume=vol),
        beat_offset=beat,
    )

song._effects = {
    "strings": lambda s, sr: reverb(s, sr, room_size=0.85, wet=0.4),
    "cello": lambda s, sr: reverb(s, sr, room_size=0.85, wet=0.35),
    "soprano": lambda s, sr: reverb(s, sr, room_size=0.9, wet=0.45),
}
