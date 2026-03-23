"""EDM vocal chop: short clipped voice hits used as percussive elements.

Vocal chops are a core EDM technique — take a vocal, chop it into tiny
fragments, and use them rhythmically. We use Junior (child-like, bright)
and Bubbles for that pitched vocal chop character.

Run: code-music samples/voices/edm_vocal_chop.py -o /tmp/vocal_chop.wav
"""

from code_music import Note, Song, Track, VoiceClip, VoiceTrack, delay, reverb

song = Song(title="edm_vocal_chop", bpm=128)

# ── EDM bed ────────────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.45))
arp = song.add_track(Track(name="arp", instrument="supersaw", volume=0.5, pan=0.2))

r = Note.rest
for _ in range(4):
    kick.extend([Note("C", 2, 1.0), Note("C", 2, 1.0), Note("C", 2, 1.0), Note("C", 2, 1.0)])
    hat.extend([Note("F", 5, 0.5)] * 8)
    arp.extend([Note("A", 4, 0.25), Note("C", 5, 0.25), Note("E", 5, 0.25), Note("A", 5, 0.25)] * 4)

# ── Vocal chops (rhythmically placed short syllables) ─────────────────────
chops = song.add_voice_track(VoiceTrack(name="chops"))

# Tight fast syllables on the 8th-note grid
syllables = [
    ("oh", "Bubbles", 200, 0.0, -0.3, 0.7),
    ("ah", "Junior", 220, 0.5, 0.3, 0.7),
    ("oh", "Bubbles", 200, 1.0, -0.3, 0.7),
    ("hey", "Junior", 200, 1.5, 0.3, 0.75),
    ("oh", "Bubbles", 200, 2.0, -0.3, 0.7),
    ("ah", "Junior", 220, 2.5, 0.3, 0.7),
    ("oh", "Bubbles", 200, 3.0, -0.3, 0.7),
    ("hey", "Superstar", 180, 3.5, 0.0, 0.8),
    # Bar 2 — shifted pattern
    ("ah", "Bubbles", 200, 4.0, 0.3, 0.7),
    ("oh", "Junior", 220, 4.5, -0.3, 0.7),
    ("yeah", "Bubbles", 190, 5.0, 0.3, 0.75),
    ("ah", "Junior", 220, 5.5, -0.3, 0.7),
    ("oh", "Bubbles", 200, 6.0, 0.0, 0.7),
    ("yeah", "Superstar", 180, 7.0, 0.0, 0.8),
]
for text, voice, rate, beat, pan_v, vol in syllables:
    chops.add(VoiceClip(text, voice=voice, rate=rate, pan=pan_v, volume=vol), beat_offset=beat)

# Repeat the pattern 4 times total by adding more
for offset in [8.0, 16.0, 24.0]:
    for text, voice, rate, beat, pan_v, vol in syllables:
        chops.add(
            VoiceClip(text, voice=voice, rate=rate, pan=pan_v, volume=vol),
            beat_offset=beat + offset,
        )

song._effects = {
    "chops": lambda s, sr: delay(
        reverb(s, sr, room_size=0.3, wet=0.15), sr, delay_ms=187.5, feedback=0.2, wet=0.15
    ),
}
