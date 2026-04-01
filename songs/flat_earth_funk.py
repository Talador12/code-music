"""flat_earth_funk.py — Funk groove using enharmonic flat note names.

Demonstrates that Bb, Eb, Ab etc. all resolve correctly via
normalize_note_name(). Clavinet funk over a classic Bb Mixolydian vamp.

Style: James Brown meets Herbie Hancock, Bb Mixolydian, 108 BPM.
"""

from code_music import Chord, Note, Song, Track, compress, reverb

song = Song(title="Flat Earth Funk", bpm=108)

BAR = 4.0
r = Note.rest

# ── Drums ──────────────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.85))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.6))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35))

for _ in range(12):
    kick.extend([Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5), r(1.0), Note("C", 2, 1.0)])
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)])
    hat.extend([Note("F#", 6, 0.5)] * 8)

# ── Bass — all flat note names ────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.7, pan=-0.1))
bass_riff = [
    Note("Bb", 2, 0.5),
    Note("Bb", 2, 0.5),
    r(0.5),
    Note("Db", 3, 0.5),
    Note("Eb", 3, 0.5),
    Note("Db", 3, 0.5),
    Note("Bb", 2, 0.5),
    r(0.5),
]
for _ in range(12):
    bass.extend(bass_riff)

# ── Clav — staccato funk chops ────────────────────────────────────────────
clav = song.add_track(Track(name="clav", instrument="pluck", volume=0.55, pan=0.2))
clav_riff = [
    Chord("Bb", "dom7", 3, duration=0.5),
    r(0.5),
    Chord("Eb", "dom7", 3, duration=0.5),
    r(0.5),
    Chord("Bb", "dom7", 3, duration=0.5),
    r(0.5),
    Chord("Ab", "dom7", 3, duration=0.5),
    r(0.5),
]
for _ in range(12):
    clav.extend(clav_riff)

# ── Lead — Bb mixolydian lick ─────────────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=0.3))
lead_lick = [
    r(8.0),  # sit out first 2 bars
    Note("Bb", 4, 0.5),
    Note("Db", 5, 0.5),
    Note("Eb", 5, 0.5),
    Note("F", 5, 0.5),
    Note("Ab", 5, 0.5),
    Note("F", 5, 0.5),
    Note("Eb", 5, 0.5),
    Note("Db", 5, 0.5),
    Note("Bb", 4, 1.0),
    r(3.0),
    Note("Db", 5, 0.5),
    Note("Eb", 5, 1.0),
    Note("F", 5, 0.5),
    Note("Ab", 5, 1.0),
    r(1.0),
]
for _ in range(3):
    lead.extend(lead_lick)

song.effects = {
    "clav": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0),
    "lead": lambda s, sr: reverb(s, sr, room_size=0.4, wet=0.15),
}
