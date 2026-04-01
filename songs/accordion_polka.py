"""accordion_polka.py — Polka. G major, 126 BPM. Beer hall bounce.

An energetic Central European polka with oom-pah bass, accordion melody,
and a bright clarinet countermelody. Bavarian beer hall on a Saturday night.

Style: Polka, G major, 2/4 time, 126 BPM.
"""

from code_music import EffectsChain, Note, Song, Track, reverb

song = Song(title="Accordion Polka", bpm=126, time_sig=(2, 4))

r = Note.rest
BAR = 2.0

# ── Tuba — oom-pah ───────────────────────────────────────────────────────
tuba = song.add_track(Track(name="tuba", instrument="bass", volume=0.6, pan=-0.1))
for _ in range(24):
    tuba.extend([Note("G", 2, 1.0), Note("D", 3, 1.0)])
    tuba.extend([Note("C", 2, 1.0), Note("E", 2, 1.0)])
    tuba.extend([Note("D", 2, 1.0), Note("A", 2, 1.0)])
    tuba.extend([Note("G", 2, 1.0), Note("B", 2, 1.0)])

# ── Snare — backbeat ─────────────────────────────────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.45))
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.65))
for _ in range(96):
    snare.extend([r(1.0), Note("E", 4, 1.0)])
    kick.extend([Note("C", 2, 1.0), r(1.0)])

# ── Accordion melody ─────────────────────────────────────────────────────
acc = song.add_track(Track(name="accordion", instrument="organ", volume=0.5, pan=0.15))
phrase_a = [
    Note("G", 4, 0.5),
    Note("A", 4, 0.5),
    Note("B", 4, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("B", 4, 0.5),
    Note("A", 4, 0.5),
    Note("G", 4, 0.5),
]
phrase_b = [
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("B", 4, 0.5),
    Note("A", 4, 0.5),
    Note("G", 4, 0.5),
    Note("A", 4, 0.5),
    Note("B", 4, 0.5),
]
phrase_c = [
    Note("D", 5, 1.0),
    Note("B", 4, 0.5),
    Note("G", 4, 0.5),
    Note("A", 4, 1.0),
    Note("G", 4, 1.0),
]
melody = phrase_a + phrase_b + phrase_c
for _ in range(8):
    acc.extend(melody)

# ── Clarinet countermelody ───────────────────────────────────────────────
clar = song.add_track(Track(name="clarinet", instrument="triangle", volume=0.35, pan=-0.2))
counter = [
    r(4.0),
    Note("B", 4, 0.5),
    Note("D", 5, 0.5),
    Note("G", 5, 0.5),
    Note("D", 5, 0.5),
    Note("E", 5, 0.5),
    Note("C", 5, 0.5),
    Note("A", 4, 1.0),
    Note("G", 4, 1.0),
    r(1.0),
]
for _ in range(8):
    clar.extend(counter)

song.effects = {
    "accordion": EffectsChain().add(reverb, room_size=0.35, wet=0.15),
    "clarinet": EffectsChain().add(reverb, room_size=0.4, wet=0.18),
}
