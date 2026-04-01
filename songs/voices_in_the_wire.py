"""voices_in_the_wire.py — Lyrics + voice synthesis showcase. Am, 95 BPM.

The first song that uses the Lyrics class end-to-end: written lyrics
auto-placed on beats, rendered through macOS say voices, mixed with
a lo-fi instrumental bed. Proves the full pipeline works.

Multiple voices: Whisper for verses (intimate), Cellos for chorus
(eerie resonance), Zarvox for the bridge (alien robot).
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    Chord,
    Lyrics,
    Note,
    Song,
    Track,
    compress,
    reverb,
    tape_sat,
)

song = Song(title="Voices in the Wire", bpm=95)

BAR = 4.0
r = Note.rest

# ── Instrumental bed — lo-fi, sparse ──────────────────────────────────────
# Rhodes pad
pad = song.add_track(Track(name="pad", instrument="rhodes", volume=0.52, pan=-0.1))
for ch, sh in [("A", "min7"), ("F", "maj7"), ("C", "maj7"), ("G", "dom7")] * 4:
    pad.add(Chord(ch, sh, 3, duration=BAR, velocity=0.5))

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.65))
bass_line = [
    Note("A", 2, HALF),
    Note("A", 2, QUARTER),
    r(QUARTER),
    Note("F", 2, HALF),
    Note("G", 2, HALF),
    Note("C", 3, HALF),
    Note("G", 2, HALF),
    Note("G", 2, HALF),
    Note("E", 2, QUARTER),
    r(QUARTER),
]
bass.extend(bass_line * 4)

# Minimal drums
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.72))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.55))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.28))

for _ in range(16):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 0.5), r(0.5), r(1.0)])
    snare.extend(
        [r(1.0), Note("D", 3, 1.0, velocity=0.5), r(1.0), Note("D", 3, 1.0, velocity=0.45)]
    )
    hat.extend([Note("F", 5, EIGHTH, velocity=0.25)] * 8)

# ── Verse vocals — Whisper voice, intimate ─────────────────────────────────
verse_lyrics = Lyrics.from_text(
    """
    every function is a phrase
    every loop becomes a rhythm
    variables hold the notes we play
    until the compiler sets them free
""",
    start_beat=0.0,
    beats_per_line=BAR,
)

verse_vox = verse_lyrics.to_voice_track(
    name="verse",
    voice="Whisper",
    backend="say",
    rate=95,
    volume=0.75,
    pan=0.0,
)
song.add_voice_track(verse_vox)

# ── Chorus vocals — Cellos voice, resonant ─────────────────────────────────
chorus_lyrics = Lyrics.from_text(
    """
    voices in the wire
    singing through the code
    every note a signal
    every song a road
""",
    start_beat=BAR * 4,
    beats_per_line=BAR,
)

chorus_vox = chorus_lyrics.to_voice_track(
    name="chorus",
    voice="Cellos",
    backend="say",
    rate=80,
    volume=0.7,
    pan=0.0,
)
song.add_voice_track(chorus_vox)

# ── Bridge vocals — Zarvox, alien robot ────────────────────────────────────
bridge_lyrics = Lyrics.from_text(
    """
    zero and one
    the smallest song
    but infinite
    when played along
""",
    start_beat=BAR * 8,
    beats_per_line=BAR,
)

bridge_vox = bridge_lyrics.to_voice_track(
    name="bridge",
    voice="Zarvox",
    backend="say",
    rate=85,
    volume=0.65,
    pan=0.0,
)
song.add_voice_track(bridge_vox)

# ── Repeat chorus at the end ──────────────────────────────────────────────
outro_lyrics = Lyrics.from_text(
    """
    voices in the wire
    singing through the code
""",
    start_beat=BAR * 12,
    beats_per_line=BAR,
)

outro_vox = outro_lyrics.to_voice_track(
    name="outro",
    voice="Cellos",
    backend="say",
    rate=75,
    volume=0.7,
    pan=0.0,
)
song.add_voice_track(outro_vox)

song.effects = {
    "pad": lambda s, sr: tape_sat(
        reverb(s, sr, room_size=0.5, wet=0.2), sr, drive=1.4, warmth=0.4, wet=0.3
    ),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
}
