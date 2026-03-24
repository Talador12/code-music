"""electric_dreams.py — Synthwave / retro-electro. Em, 110 BPM.

Second synthwave track — slipstream.py is Kavinsky-dark, this is
more Perturbator/Lazerhawk: faster, slightly more aggressive, still
that 80s retro-future feel. Gated reverb snare (the defining sound),
arpeggio synthesizer, pulsing bass.
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
    compress,
    conv_reverb,
    delay,
    gate,
    reverb,
    stereo_width,
)

song = Song(title="Electric Dreams", bpm=110)

BAR = 4.0
r = Note.rest

# ── Kit ────────────────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.95))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.88))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.42))

kick.extend([r(BAR)] * 4)
snare.extend([r(BAR)] * 4)
hat.extend([r(BAR)] * 4)

for _ in range(20):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])
    hat.extend([Note("F", 5, EIGHTH)] * 8)

kick.extend([r(BAR)] * 4)
snare.extend([r(BAR)] * 4)
hat.extend([r(BAR)] * 4)

# ── Arp synth ─────────────────────────────────────────────────────────────
arp_tr = song.add_track(Track(name="arp", instrument="square", volume=0.52, pan=0.2))
arp_tr.extend([r(BAR)] * 4)
for _ in range(5):
    for ch, sh in [("E", "min7"), ("C", "maj7"), ("G", "maj"), ("B", "dom7")] * 4:
        arp_tr.extend(arp(Chord(ch, sh, 4), pattern="up", rate=EIGHTH, octaves=2))
arp_tr.extend([r(BAR)] * 4)

# ── Lead ──────────────────────────────────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.58, pan=-0.1))
lead.extend([r(BAR)] * 12)
lead_mel = [
    Note("E", 5, QUARTER),
    r(EIGHTH),
    Note("D", 5, EIGHTH),
    Note("B", 4, HALF),
    Note("C", 5, QUARTER),
    Note("D", 5, QUARTER),
    r(HALF),
    Note("G", 5, QUARTER),
    Note("F#", 5, QUARTER),
    Note("E", 5, HALF),
    Note("B", 4, WHOLE),
]
lead.extend(lead_mel * 4)
lead.extend([r(BAR)] * 4)

# ── Bass ──────────────────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="sawtooth", volume=0.70))
bass.extend([r(BAR)] * 4)
bass_pat = [
    Note("E", 2, QUARTER),
    Note("E", 2, EIGHTH),
    r(EIGHTH),
    Note("C", 2, QUARTER),
    r(QUARTER),
    Note("G", 2, QUARTER),
    Note("B", 2, EIGHTH),
    Note("E", 2, EIGHTH),
    Note("B", 1, HALF),
]
bass.extend(bass_pat * 20)
bass.extend([r(BAR)] * 4)

# ── Pad ────────────────────────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="strings", volume=0.32, pan=0.3))
pad.extend([r(BAR)] * 8)
for ch, sh in [("E", "min"), ("C", "maj"), ("G", "maj"), ("B", "dom7")] * 6:
    pad.add(Chord(ch, sh, 3, duration=BAR, velocity=0.38))
pad.extend([r(BAR)] * 4)

song._effects = {
    "snare": lambda s, sr: gate(
        conv_reverb(s, sr, room="plate", wet=0.7),
        sr,
        rate_hz=1.8,
        shape="square",
        duty=0.35,
    ),
    "arp": lambda s, sr: delay(s, sr, delay_ms=272.0, feedback=0.32, wet=0.22, ping_pong=True),
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.7, wet=0.3), width=1.6),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
}
