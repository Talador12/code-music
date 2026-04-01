"""samba_de_janeiro.py — Samba. G major, 108 BPM. Rio carnival energy.

A classic samba pattern with syncopated percussion, nylon guitar chords,
and a bright brass-like lead. Uses the partido alto rhythmic feel.

Style: Brazilian samba, G major, 108 BPM.
"""

from code_music import Chord, Note, Song, Track, reverb

song = Song(title="Samba de Janeiro", bpm=108)

r = Note.rest
BAR = 4.0

# ── Drums — samba groove ──────────────────────────────────────────────────
kick = song.add_track(Track(name="surdo", instrument="drums_kick", volume=0.75))
snare = song.add_track(Track(name="tamborim", instrument="drums_snare", volume=0.45))
hat = song.add_track(Track(name="shaker", instrument="drums_hat", volume=0.3))

for _ in range(16):
    # Surdo: bass on 2 and 4
    kick.extend([r(1.0), Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0)])
    # Tamborim: partido alto pattern
    snare.extend(
        [
            Note("E", 4, 0.5),
            r(0.5),
            Note("E", 4, 0.5),
            Note("E", 4, 0.5),
            r(0.5),
            Note("E", 4, 0.5),
            r(0.5),
            Note("E", 4, 0.5),
        ]
    )
    # Shaker: steady 16ths
    hat.extend([Note("F#", 6, 0.25)] * 16)

# ── Guitar — nylon strum chords ──────────────────────────────────────────
guitar = song.add_track(Track(name="guitar", instrument="pluck", volume=0.45, pan=-0.2))
prog = [
    Chord("G", "maj", 3, duration=2.0),
    Chord("G", "maj", 3, duration=1.0),
    r(1.0),
    Chord("C", "maj", 3, duration=2.0),
    Chord("D", "dom7", 3, duration=1.0),
    r(1.0),
]
for _ in range(16):
    guitar.extend(prog)

# ── Bass — syncopated root movement ──────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6, pan=-0.1))
bass_riff = [
    Note("G", 2, 0.5),
    r(0.5),
    Note("G", 2, 0.5),
    Note("B", 2, 0.5),
    Note("D", 3, 0.5),
    Note("B", 2, 0.5),
    Note("G", 2, 0.5),
    r(0.5),
]
for _ in range(16):
    bass.extend(bass_riff)

# ── Lead — bright melodic theme ──────────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=0.25))
melody_a = [
    Note("D", 5, 0.5),
    Note("B", 4, 0.5),
    Note("G", 4, 0.5),
    Note("A", 4, 0.5),
    Note("B", 4, 1.0),
    Note("D", 5, 1.0),
]
melody_b = [
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("B", 4, 0.5),
    Note("A", 4, 1.0),
    Note("G", 4, 1.0),
]
for _ in range(8):
    lead.extend(melody_a + melody_b)

song._effects = {
    "guitar": lambda s, sr: reverb(s, sr, room_size=0.35, wet=0.15),
    "lead": lambda s, sr: reverb(s, sr, room_size=0.4, wet=0.2),
}
