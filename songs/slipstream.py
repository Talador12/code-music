"""slipstream.py — Electro / synthwave. Dm, 118 BPM. Retro 80s feel.

Synthwave is nostalgia for a future that never happened. Arpeggiated
synthesizers, gated reverb snare, big bass. Kavinsky, Perturbator,
Carpenter Brut, Daft Punk's Tron Legacy score. Slightly melancholic,
very cinematic, extremely cool.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    WHOLE,
    Chord,
    Note,
    Song,
    Track,
    arp,
    chorus,
    delay,
    gate,
    reverb,
    stereo_width,
)

song = Song(title="Slipstream", bpm=118)

BAR = 4.0
r = Note.rest

# ── Kick — four on floor, synthwave style ─────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.95))
kick.extend([r(BAR)] * 4)
kick.extend([Note("C", 2, 1.0)] * (24 * 4))
kick.extend([r(BAR)] * 4)

# ── Gated reverb snare — the synthwave signature ──────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.85))
snare.extend([r(BAR)] * 4)
snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)] * 24)
snare.extend([r(BAR)] * 4)

# ── Arpeggio synth — the hook ─────────────────────────────────────────────
arp_tr = song.add_track(Track(name="arp", instrument="sawtooth", volume=0.55, pan=0.15))
arp_tr.extend([r(BAR)] * 4)
for ch, sh in [("D", "min7"), ("A#", "maj7"), ("F", "maj7"), ("C", "dom7")] * 6:
    arp_tr.extend(arp(Chord(ch, sh, 4), pattern="up_down", rate=EIGHTH, octaves=2))
arp_tr.extend([r(BAR)] * 4)

# ── Saw bass — lock to kick ────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="sawtooth", volume=0.72))
bass.extend([r(BAR)] * 4)
bass_line = [
    Note("D", 2, 1.0),
    Note("D", 2, 0.5),
    r(0.5),
    Note("A#", 1, 0.5),
    r(0.5),
    Note("F", 2, 0.5),
    r(0.5),
    Note("C", 2, 0.5),
    Note("D", 2, 0.5),
    r(1.0),
    Note("D", 2, 2.0),
]
bass.extend(bass_line * 6)
bass.extend([r(BAR)] * 4)

# ── Lead — arpeggiated on top ─────────────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="supersaw", volume=0.5, pan=-0.1))
lead.extend([r(BAR)] * 12)
lead_mel = [
    Note("D", 5, QUARTER),
    r(EIGHTH),
    Note("F", 5, EIGHTH),
    Note("A", 5, HALF),
    Note("C", 6, QUARTER),
    Note("A#", 5, QUARTER),
    Note("A", 5, HALF),
    r(QUARTER),
    Note("G", 5, QUARTER),
    Note("F", 5, QUARTER),
    Note("E", 5, QUARTER),
    Note("D", 5, WHOLE),
]
lead.extend(lead_mel * 4)
lead.extend([r(BAR)] * 4)

# ── Retro string pad ──────────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="strings", volume=0.38, pan=0.3))
pad.extend([r(BAR)] * 8)
for ch, sh in [("D", "min7"), ("A#", "maj7"), ("F", "maj7"), ("C", "dom7")] * 5:
    pad.add(Chord(ch, sh, 3, duration=BAR, velocity=0.42))
pad.extend([r(BAR)] * 4)

song._effects = {
    "snare": lambda s, sr: gate(
        reverb(s, sr, room_size=0.9, wet=0.6), sr, rate_hz=2.0, shape="square", duty=0.4
    ),
    "arp": lambda s, sr: delay(s, sr, delay_ms=254.0, feedback=0.35, wet=0.25, ping_pong=True),
    "lead": lambda s, sr: chorus(reverb(s, sr, room_size=0.5, wet=0.2), sr, rate_hz=0.5, wet=0.2),
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.7, wet=0.35), width=1.6),
}
