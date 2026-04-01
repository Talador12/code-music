"""teardrop.py — Trip-hop. Dm, 80 BPM. Massive Attack / Portishead territory.

Slow. Heavy. The beat barely moves but it weighs a ton. Sub bass,
breakbeat-influenced drums at half speed, a piano that plays like
it's underwater. Everything has that Bristol sound — dub influence
filtered through electronica. Space between notes is the instrument.
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
    delay,
    humanize,
    lowpass,
    reverb,
    stereo_width,
    tape_sat,
)

song = Song(title="Teardrop", bpm=80)

BAR = 4.0
r = Note.rest
E8 = EIGHTH

# ── Sub bass — the weight ─────────────────────────────────────────────────
sub = song.add_track(Track(name="sub", instrument="sub_bass", volume=0.82))
sub.extend(
    [
        Note("D", 1, HALF),
        r(QUARTER),
        Note("D", 1, QUARTER),
        Note("F", 1, HALF),
        r(HALF),
        Note("C", 1, HALF),
        Note("D", 1, HALF),
        Note("A", 0, WHOLE),
    ]
    * 4
)

# ── Trip-hop beat — breakbeat-influenced, sparse ──────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.9))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.75))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3))

# Syncopated, not 4-on-the-floor — trip-hop signature
for _ in range(16):
    kick.extend([Note("C", 2, E8), r(E8), r(QUARTER), r(E8), Note("C", 2, E8), r(QUARTER)])
    snare.extend(
        [r(1.0), Note("D", 3, 1.0, velocity=0.7), r(1.0), Note("D", 3, 0.5, velocity=0.55), r(0.5)]
    )
    hat.extend([Note("F", 5, E8, velocity=0.25)] * 8)

# ── Piano — underwater, lots of space ─────────────────────────────────────
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.55, pan=-0.1))
piano.extend([r(BAR)] * 4)
phrase = humanize(
    [
        Note("D", 4, QUARTER),
        r(E8),
        Note("F", 4, E8),
        Note("A", 4, HALF),
        r(BAR),
        Note("G", 4, QUARTER),
        r(QUARTER),
        Note("F", 4, HALF),
        r(HALF),
        Note("E", 4, QUARTER),
        r(QUARTER),
        Note("D", 4, WHOLE),
        r(BAR),
    ],
    vel_spread=0.09,
    timing_spread=0.06,
)
piano.extend(phrase * 2)

# ── Strings — very quiet, just texture ─────────────────────────────────────
strings = song.add_track(Track(name="strings", instrument="strings", volume=0.28, pan=0.25))
strings.extend([r(BAR)] * 8)
for ch, sh in [("D", "min7"), ("F", "maj7"), ("C", "maj7"), ("A", "dom7")] * 2:
    strings.add(Chord(ch, sh, 3, duration=BAR, velocity=0.35))

song.effects = {
    "sub": lambda s, sr: lowpass(s, sr, cutoff_hz=100.0),
    "piano": lambda s, sr: tape_sat(
        delay(reverb(s, sr, room_size=0.6, wet=0.25), sr, delay_ms=375.0, feedback=0.3, wet=0.2),
        sr,
        drive=1.3,
        warmth=0.5,
        wet=0.25,
    ),
    "strings": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.8, wet=0.4), width=1.7),
}
