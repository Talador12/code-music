"""clarity_drive.py — Zedd-inspired big-room electro.

Style cues:
- Anthemic 4-chord loop (Am - F - C - G) driving the whole track
- Punchy four-on-the-floor kick with sidechained feel (handled via compressor)
- Bright sawtooth supersaw lead melody that peaks in the chorus drop
- Classic breakdown → buildup → drop structure
- Driving eighth-note bass in drop sections
- Lush pad underneath everything, panned slightly wide

Structure (bars):
  1-4   Intro: pads only
  5-8   Verse: add bass + hat
  9-12  Pre-chorus: add chord stabs + rising lead
  13-16 Drop / Chorus: full texture — kick, bass, lead, pads, hats
  17-20 Breakdown: strip to pads + melody ghost
  21-24 Build: bring layers back one by one
  25-32 Second drop: full + extra arp layer
  33-36 Outro: pads fade
"""

from code_music import Chord, Note, Song, Track, compress, delay, reverb

song = Song(title="Offshore", bpm=128)

# ── helpers ──────────────────────────────────────────────────────────────────
BAR = 4.0  # beats per bar


def repeat(events, n):
    return events * n


# Chord loop: Am - F - C - G (one bar each)
AM = Chord("A", "min", 3, duration=BAR, velocity=0.65)
FM = Chord("F", "maj7", 3, duration=BAR, velocity=0.65)
CM = Chord("C", "maj", 3, duration=BAR, velocity=0.65)
GM = Chord("G", "dom7", 3, duration=BAR, velocity=0.65)
LOOP = [AM, FM, CM, GM]

# ── Pad — always present, slow attack, slightly left ─────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.15))
pad.extend(repeat(LOOP, 9))  # 36 bars

# ── Kick — four on floor, starts bar 5 ───────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
k = Note("C", 2, 1.0)
r = Note.rest
kick.extend(repeat([r(BAR)], 4))  # intro silence
kick.extend(repeat([k, k, k, k], 28))  # bars 5-32
kick.extend(repeat([r(BAR)], 4))  # outro silence

# ── Snare / clap — 2 & 4, starts bar 5 ──────────────────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.7))
s = Note("D", 3, 1.0)
snare.extend(repeat([r(BAR)], 4))
snare.extend(repeat([r(1.0), s, r(1.0), s], 28))
snare.extend(repeat([r(BAR)], 4))

# ── Hi-hat — 8th notes, starts bar 5 ─────────────────────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.45))
h = Note("F", 5, 0.5)
hat.extend(repeat([r(BAR)], 4))
hat.extend(repeat([h] * 8, 28))
hat.extend(repeat([r(BAR)], 4))

# ── Bass — driving 8ths in drop sections (bars 5-8, 13-16, 25-32) ─────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.75, pan=0.0))
bass_note = [Note("A", 2, 0.5), Note("A", 2, 0.5)]  # 8th pumping bass
bass_root = {  # root per bar
    "Am": Note("A", 2, 0.5),
    "F": Note("F", 2, 0.5),
    "C": Note("C", 3, 0.5),
    "G": Note("G", 2, 0.5),
}
roots = ["Am", "F", "C", "G"]

# silence: bars 1-4
bass.extend(repeat([r(BAR)], 4))
# verse bars 5-8: quarter-note root
for root in roots:
    bass.add(Note(bass_root[root].pitch, bass_root[root].octave, 1.0, velocity=0.7))
    bass.extend(repeat([r(1.0)], 3))
# pre-chorus bars 9-12: silence (builds tension)
bass.extend(repeat([r(BAR)], 4))
# drop bars 13-16: 8th pumping bass
for root in roots:
    n = bass_root[root]
    bass.extend([Note(n.pitch, n.octave, 0.5, velocity=0.85)] * 8)
# breakdown bars 17-20: quiet root only
for root in roots:
    n = bass_root[root]
    bass.add(Note(n.pitch, n.octave, 1.0, velocity=0.4))
    bass.extend(repeat([r(1.0)], 3))
# build bars 21-24: root + octave answer
for root in roots:
    n = bass_root[root]
    bass.add(Note(n.pitch, n.octave, 0.5, velocity=0.6))
    bass.add(Note(n.pitch, n.octave + 1, 0.5, velocity=0.6))
    bass.extend(repeat([r(1.0)], 3))
# second drop bars 25-32: full 8th pump
for _ in range(2):
    for root in roots:
        n = bass_root[root]
        bass.extend([Note(n.pitch, n.octave, 0.5, velocity=0.9)] * 8)
# outro bars 33-36
bass.extend(repeat([r(BAR)], 4))

# ── Lead melody — sawtooth, starts bar 9, right-pan ──────────────────────────
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.6, pan=0.2))
lead.extend(repeat([r(BAR)], 8))  # silent bars 1-8

# Pre-chorus ascending phrase (bars 9-12)
pre_chorus = [
    Note("A", 4, 0.5),
    Note("C", 5, 0.5),
    Note("E", 5, 1.0),
    Note("C", 5, 0.5),
    Note("A", 4, 0.5),
    Note.rest(1.0),
    Note("F", 4, 0.5),
    Note("A", 4, 0.5),
    Note("C", 5, 1.0),
    Note("E", 5, 2.0),
    Note.rest(2.0),
    Note("G", 4, 0.5),
    Note("B", 4, 0.5),
    Note("D", 5, 1.0),
    Note("F", 5, 2.0),
    Note.rest(2.0),
    Note("A", 5, 1.0),
    Note("G", 5, 0.5),
    Note("E", 5, 0.5),
    Note("C", 5, 1.0),
    Note("A", 4, 1.0),
    Note.rest(2.0),
]
lead.extend(pre_chorus)

# Drop chorus melody (bars 13-16) — the money riff
drop_melody = [
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("E", 5, 0.5),
    Note("C", 5, 0.5),
    Note("D", 5, 1.0),
    Note("E", 5, 1.0),
    Note("F", 5, 0.5),
    Note("E", 5, 0.5),
    Note("C", 5, 0.5),
    Note("A", 4, 0.5),
    Note("G", 4, 2.0),
    Note("C", 5, 0.5),
    Note("E", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 1.0),
    Note("E", 5, 1.0),
    Note("F", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A", 5, 1.0),
    Note("A", 5, 2.0),
]
lead.extend(drop_melody)

# Breakdown ghost melody (bars 17-20) — quiet, high, sparse
ghost = [
    Note("E", 5, 0.5, velocity=0.3),
    Note.rest(0.5),
    Note("A", 5, 1.0, velocity=0.3),
    Note.rest(2.0),
    Note("C", 5, 0.5, velocity=0.3),
    Note.rest(0.5),
    Note("G", 5, 1.0, velocity=0.3),
    Note.rest(2.0),
    Note("F", 5, 0.5, velocity=0.3),
    Note.rest(3.5),
    Note.rest(BAR),
]
lead.extend(ghost)

# Build re-entry (bars 21-24) — same as pre-chorus but louder
lead.extend(pre_chorus)

# Second drop extended (bars 25-32) — play melody twice
lead.extend(drop_melody)
lead.extend(drop_melody)

# Outro silence
lead.extend(repeat([r(BAR)], 4))

# ── Arp — only in second drop (bars 25-32), panned right ─────────────────────
arp = song.add_track(Track(name="arp", instrument="pluck", volume=0.45, pan=0.6))
arp.extend(repeat([r(BAR)], 24))  # silent first 24 bars
am_arp = [Note("A", 4, 0.25), Note("C", 5, 0.25), Note("E", 5, 0.25), Note("A", 5, 0.25)]
f_arp = [Note("F", 4, 0.25), Note("A", 4, 0.25), Note("C", 5, 0.25), Note("F", 5, 0.25)]
c_arp = [Note("C", 4, 0.25), Note("E", 4, 0.25), Note("G", 4, 0.25), Note("C", 5, 0.25)]
g_arp = [Note("G", 3, 0.25), Note("B", 3, 0.25), Note("D", 4, 0.25), Note("G", 4, 0.25)]
for _ in range(2):
    for arp_pat in [am_arp, f_arp, c_arp, g_arp]:
        arp.extend(arp_pat * 4)
arp.extend(repeat([r(BAR)], 4))

# ── Post-render effects applied in render hook ────────────────────────────────
# Effects are applied after rendering. Attach a post_render hook to the song.
# Here we mark which tracks get which treatment.
# (see render.py / Makefile for how post_render is called)
# pad → reverb (room=0.7, wet=0.3)
# lead → delay (375ms ping-pong, feedback=0.3)
# arp → chorus + reverb

song.effects = {
    "pad": lambda s, sr: reverb(s, sr, room_size=0.7, wet=0.3),
    "lead": lambda s, sr: delay(s, sr, delay_ms=375.0, feedback=0.3, wet=0.25, ping_pong=True),
    "arp": lambda s, sr: reverb(compress(s, sr, ratio=3.0, wet=0.5), sr, room_size=0.5, wet=0.2),
}
