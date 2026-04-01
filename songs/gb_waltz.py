"""gb_waltz.py — Waltz in Gb major using enharmonic flat names throughout.

A gentle 3/4 waltz that exercises normalize_note_name with Gb, Cb, Fb —
the rarely-used enharmonics. Piano melody over a simple oom-pah-pah bass.

Style: Romantic waltz, Gb major, 3/4 time, 126 BPM.
"""

from code_music import Chord, Note, Song, Track, reverb

song = Song(title="Gb Waltz", bpm=126, time_sig=(3, 4))

r = Note.rest
BAR = 3.0  # 3/4 time

# ── Left hand — oom-pah-pah ────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="piano", volume=0.55, pan=-0.3))
pah = song.add_track(Track(name="pah", instrument="piano", volume=0.4, pan=0.1))

progression = [
    ("Gb", "maj", "Gb"),
    ("Db", "maj", "Db"),
    ("Eb", "min", "Eb"),
    ("Cb", "maj", "Cb"),
]

for _ in range(6):
    for root, shape, bass_note in progression:
        bass.extend([Note(bass_note, 2, 1.0), r(2.0)])
        pah.extend(
            [r(1.0), Chord(root, shape, 3, duration=1.0), Chord(root, shape, 3, duration=1.0)]
        )

# ── Melody — Gb major pentatonic feel ──────────────────────────────────────
melody = song.add_track(Track(name="melody", instrument="piano", volume=0.65, pan=0.2))
phrases = [
    [Note("Gb", 4, 1.5), Note("Ab", 4, 0.75), Note("Bb", 4, 0.75)],
    [Note("Db", 5, 1.5), Note("Bb", 4, 1.5)],
    [Note("Ab", 4, 1.0), Note("Gb", 4, 1.0), Note("Eb", 4, 1.0)],
    [Note("Gb", 4, 2.0), r(1.0)],
]

for _ in range(6):
    for phrase in phrases:
        melody.extend(phrase)

song.effects = {
    "melody": lambda s, sr: reverb(s, sr, room_size=0.55, wet=0.25),
    "bass": lambda s, sr: reverb(s, sr, room_size=0.4, wet=0.15),
}
