"""deadmau5_house.py — deadmau5 style progressive house.

Style: Strobe / Ghosts 'n' Stuff era. Slow chord evolution, minimal percussion,
one synth idea developed over many bars. The music is patient.

Key deadmau5 signatures:
  - Very long structures (the full track is patient)
  - Single supersaw pad chord that slowly filters open
  - Simple 4-on-the-floor kick + offbeat hat
  - That iconic pluck/lead arp that enters and becomes the whole track
  - Minimal bass: root note, nothing fancy
  - The drop is just the filter opening, not adding new elements

Structure (128 BPM, F minor):
  Bars 1-8:    Intro — silent except kick
  Bars 9-16:   Pad enters, filter closed (dark)
  Bars 17-24:  Arp enters at low volume, filter slowly opens
  Bars 25-32:  Lead melody emerges from the arp texture
  Bars 33-40:  Everything present — this IS the drop
  Bars 41-48:  Gradual strip-back
  Bars 49-56:  Pad only, filter closes again
  Bars 57-60:  Kick alone → end
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    chord_prog,
    compress,
    crescendo,
    decrescendo,
    delay,
    lfo_filter,
    reverb,
    stereo_width,
)

song = Song(title="Machine Dreams", bpm=128)

BAR = 4.0
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── Chord loop: Fm - Db - Ab - Eb ────────────────────────────────────────
ROOTS = ["F", "C#", "G#", "D#"]
SHAPES = ["min7", "maj7", "maj7", "dom7"]
PROG = chord_prog(ROOTS, SHAPES, octave=3, duration=BAR * 2, velocity=0.5)  # 2 bars per chord

# ── Kick — 4-on-floor, whole track ───────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
kick.extend([Note("C", 2, 1.0)] * (60 * 4))

# ── Hat — offbeat 8ths ───────────────────────────────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35))
hat.extend(bars(8))
hat.extend([r(0.5), Note("F", 5, 0.5)] * (52 * 4))

# ── Bass — root only, quiet ───────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6, pan=0.0))
bass.extend(bars(16))
bass_roots = [("F", 2), ("C#", 2), ("G#", 1), ("D#", 2)]
for _ in range(5):
    for p, o in bass_roots:
        bass.extend([Note(p, o, BAR * 2, velocity=0.65)])
bass.extend(bars(4))

# ── Supersaw pad — enters bar 9, filter controlled via effect ────────────
pad = song.add_track(Track(name="pad", instrument="supersaw", volume=0.5, pan=0.0))
pad.extend(bars(8))
for _ in range(6):
    pad.extend(PROG)
pad.extend(bars(8))

# ── Pluck arp — enters bar 17, very quiet, builds ────────────────────────
arp_tr = song.add_track(Track(name="arp", instrument="pluck", volume=0.0, pan=-0.2))
arp_tr.extend(bars(16))
# Volume builds across bars 17-56
arp_notes = []
for bar_i in range(40):
    vol = 0.1 + bar_i * (0.6 / 40)  # 0.1 → 0.7 over 40 bars
    chord_idx = (bar_i // 2) % 4
    roots_map = {"F": "F", "C#": "C#", "G#": "G#", "D#": "D#"}
    r_note = ROOTS[chord_idx]
    c = Chord(r_note, SHAPES[chord_idx], 4, duration=0.25)
    arp_notes.extend([Note(n.pitch, duration=0.25, velocity=vol) for n in c.notes[:3]] + [r(0.25)])
arp_tr.extend(arp_notes)
arp_tr.extend(bars(4))

# ── Lead melody — emerges from the arp, bars 25-48 ───────────────────────
lead = song.add_track(Track(name="lead", instrument="lead_edm", volume=0.0, pan=0.15))
lead.extend(bars(24))
# Build from whisper to full volume
lead_melody_base = [
    Note("F", 5, 0.5),
    Note("G#", 5, 0.5),
    Note("A#", 5, 1.0),
    Note("C", 6, 0.5),
    Note("A#", 5, 0.5),
    Note("G#", 5, 1.0),
    Note("F", 5, 0.5),
    Note("G#", 5, 0.25),
    Note("A#", 5, 0.25),
    Note("C", 6, 1.0),
    Note("F", 5, 1.0),
    r(1.0),
    Note("D#", 5, 0.5),
    Note("F", 5, 0.5),
    Note("G#", 5, 1.0),
    Note("A#", 5, 0.5),
    Note("G#", 5, 0.5),
    Note("F", 5, 2.0),
]
mel_section = crescendo(lead_melody_base * 3, start_vel=0.15, end_vel=0.85)
lead.extend(mel_section[: len(lead_melody_base) * 2])  # bars 25-32 quiet
lead.extend(crescendo(lead_melody_base * 2, 0.8, 0.95))  # bars 33-40 full
lead.extend(decrescendo(lead_melody_base * 2, 0.9, 0.2))  # bars 41-48 fade
lead.extend(bars(12))

# ── Effects ────────────────────────────────────────────────────────────────
# The pad effect simulates the classic deadmau5 LP filter automation:
# bars 9-16 = dark (500 Hz), bars 17-40 = slowly opening, bars 41-56 = dark again
# We approximate with lfo_filter at very slow rate
song._effects = {
    "pad": lambda s, sr: stereo_width(
        lfo_filter(
            reverb(s, sr, room_size=0.5, wet=0.2),
            sr,
            rate_hz=0.008,
            min_cutoff=300.0,
            max_cutoff=8000.0,
        ),
        width=1.7,
    ),
    "lead": lambda s, sr: delay(s, sr, delay_ms=234.0, feedback=0.35, wet=0.25, ping_pong=True),
    "arp": lambda s, sr: reverb(s, sr, room_size=0.5, wet=0.2),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
}
