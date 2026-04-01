"""trap_god.py — Trap / Atlanta hip-hop production. Gm, 140 BPM half-time.

808 sub bass, hi-hat triplet rolls, snare on 3, punchy kick.
Metro Boomin / Southside / Murda Beatz aesthetic — space, 808s,
that one haunting melody floating above drums that sound like they
cost more than most people's rent.

Half-time feel at 140 BPM = 70 BPM groove with 140 BPM hats.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    SIXTEENTH,
    Chord,
    Note,
    Song,
    Track,
    compress,
    delay,
    lowpass,
    reverb,
    stereo_width,
)

song = Song(title="Trap God", bpm=140)

BAR = 4.0
r = Note.rest


def b(n):
    return [r(BAR)] * n


# ── 808 sub bass — the whole identity of this genre ──────────────────────
sub = song.add_track(Track(name="808", instrument="drums_808", volume=0.98))
pattern_808 = [
    Note("G", 1, HALF, velocity=0.95),
    Note("G", 1, QUARTER, velocity=0.85),
    r(QUARTER),
    Note("D#", 1, QUARTER, velocity=0.9),
    r(QUARTER),
    Note("F", 1, HALF, velocity=0.88),
]
sub.extend(b(2))
sub.extend(pattern_808 * 10)
sub.extend(b(2))

# ── Kick — sparse, hits hard on 1 only ───────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
kick_pat = [Note("C", 2, 1.0, velocity=0.98), r(3.0)]  # kick on 1 only
kick.extend(b(2))
kick.extend(kick_pat * 10)
kick.extend(b(2))

# ── Snare / clap — beat 3 (half-time) ────────────────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_clap", volume=0.88))
snare_pat = [r(2.0), Note("D", 3, 1.0, velocity=0.92), r(1.0)]
snare.extend(b(2))
snare.extend(snare_pat * 10)
snare.extend(b(2))

# ── Hi-hat triplet rolls — the trap signature ─────────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.52))
hat.extend(b(2))
# Standard 8ths with triplet bursts every bar
hat_bar_a = [Note("F", 5, EIGHTH)] * 8  # straight 8ths
hat_bar_b = (  # triplet roll + straight
    [Note("F", 5, SIXTEENTH / 1.5)] * 6  # triplet 16ths
    + [Note("F", 5, EIGHTH)] * 5
)
for i in range(10):
    hat.extend(hat_bar_b if i % 2 == 1 else hat_bar_a)
hat.extend(b(2))

# ── Haunting melody — supersaw lead, very sparse ─────────────────────────
lead = song.add_track(Track(name="lead", instrument="supersaw", volume=0.42, pan=0.1))
lead.extend(b(2))
mel = [
    Note("G", 4, QUARTER),
    r(QUARTER),
    Note("D#", 4, HALF),
    r(BAR),
    Note("F", 4, QUARTER),
    r(QUARTER),
    Note("D", 4, QUARTER),
    r(QUARTER),
    Note("G", 4, HALF),
    r(HALF),
    r(BAR),
    Note("A#", 4, QUARTER),
    r(QUARTER),
    Note("G", 4, HALF),
    r(BAR),
    Note("D", 5, QUARTER),
    Note("C", 5, QUARTER),
    Note("A#", 4, HALF),
    r(BAR),
]
lead.extend(mel * 2 + mel[: len(mel) // 2])
lead.extend(b(2))

# ── Dark pad — barely present ─────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.22, pan=-0.1))
pad.extend(b(2))
for ch, sh in [("G", "min7"), ("D#", "maj7"), ("F", "dom7"), ("C", "min7")] * 3:
    pad.add(Chord(ch, sh, 3, duration=BAR, velocity=0.35))
pad.extend(b(2))

song.effects = {
    "808": lambda s, sr: lowpass(
        compress(s, sr, threshold=0.4, ratio=6.0, makeup_gain=1.3), sr, cutoff_hz=120.0
    ),
    "lead": lambda s, sr: delay(s, sr, delay_ms=214.0, feedback=0.3, wet=0.2, ping_pong=True),
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.7, wet=0.35), width=1.8),
}
