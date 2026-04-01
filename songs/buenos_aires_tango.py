"""buenos_aires_tango.py — Argentine tango. D minor, 66 BPM. Bandoneon and strings.

A melancholic tango with the classic habanera bass, legato bandoneon melody,
and pizzicato strings. Piazzolla-adjacent but traditional in structure.

Style: Argentine tango, Dm, 66 BPM.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    delay,
    reverb,
)

song = Song(title="Buenos Aires Tango", bpm=66)

r = Note.rest

# ── Bass — habanera pattern ───────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="contrabass", volume=0.6, pan=-0.15))
habanera = [Note("D", 2, 1.5), Note("A", 2, 0.5), Note("D", 2, 1.0), Note("A", 2, 1.0)]
for _ in range(12):
    bass.extend(habanera)

# ── Bandoneon (pad as proxy) — legato melody ─────────────────────────────
bandoneon = song.add_track(Track(name="bandoneon", instrument="organ", volume=0.55, pan=0.1))
melody_a = [
    Note("D", 4, 1.0),
    Note("F", 4, 0.5),
    Note("A", 4, 0.5),
    Note("G", 4, 1.0),
    Note("F", 4, 1.0),
    Note("E", 4, 1.5),
    Note("D", 4, 0.5),
    Note("C#", 4, 1.0),
    Note("D", 4, 1.0),
]
melody_b = [
    Note("A", 4, 1.0),
    Note("G", 4, 0.5),
    Note("F", 4, 0.5),
    Note("E", 4, 1.0),
    Note("D", 4, 1.0),
    Note("F", 4, 1.5),
    Note("E", 4, 0.5),
    Note("D", 4, 2.0),
]
for _ in range(3):
    bandoneon.extend(melody_a + melody_b)

# ── Strings — sustained chords ───────────────────────────────────────────
strings = song.add_track(Track(name="strings", instrument="pad", volume=0.35, pan=0.0))
chords = [
    Chord("D", "min", 3, duration=8.0),
    Chord("A", "dom7", 3, duration=8.0),
    Chord("Bb", "maj", 3, duration=8.0),
    Chord("A", "dom7", 3, duration=8.0),
]
for _ in range(3):
    strings.extend(chords)

# ── Pizzicato accent ─────────────────────────────────────────────────────
pizz = song.add_track(Track(name="pizz", instrument="pluck", volume=0.3, pan=0.25))
pizz_riff = [r(1.0), Note("D", 4, 0.5), r(0.5), Note("A", 3, 0.5), r(1.5)]
for _ in range(12):
    pizz.extend(pizz_riff)

song.effects = {
    "bandoneon": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
    "strings": EffectsChain().add(reverb, room_size=0.7, wet=0.3),
    "pizz": EffectsChain().add(delay, delay_ms=450, feedback=0.15, wet=0.12),
}
