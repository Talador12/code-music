"""silk_road.py — World / Experimental. Persian scale, Am, 88 BPM.

Third track for Wrong Octave album. The Persian scale (1 b2 3 4 b5 b6 7)
has two augmented seconds and a tritone where you don't expect it.
This track uses the koto_ks for melody and sitar_ks for countermelody,
with a tabla pattern and a contrabass drone. Ancient routes. Strange beauty.
"""

from code_music import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    WHOLE,
    Note,
    Song,
    Track,
    crescendo,
    decrescendo,
    delay,
    humanize,
    lowpass,
    reverb,
    scale,
)

song = Song(title="Silk Road", bpm=88)

BAR = 4.0
r = Note.rest

# ── Tanpura-style drone — A and E ─────────────────────────────────────────
for pitch, oct, pan_v in [("A", 1, 0.0), ("E", 2, 0.1)]:
    drone = song.add_track(Track(name=f"drone_{pitch}", instrument="sine", volume=0.22, pan=pan_v))
    for _ in range(24):
        drone.add(Note(pitch, oct, BAR, velocity=0.45))

# ── Tabla — cross-rhythm pattern ──────────────────────────────────────────
tabla = song.add_track(Track(name="tabla", instrument="tabla", volume=0.65))
tala = humanize(
    [
        Note("A", 4, EIGHTH, velocity=0.85),
        Note("A", 4, EIGHTH, velocity=0.55),
        r(EIGHTH),
        Note("A", 4, EIGHTH, velocity=0.75),
        Note("A", 4, EIGHTH, velocity=0.6),
        r(EIGHTH),
        Note("A", 4, EIGHTH, velocity=0.8),
        Note("A", 4, EIGHTH, velocity=0.5),
    ],
    vel_spread=0.12,
)
for _ in range(24):
    tabla.extend(tala)

# ── Koto KS — Persian scale melody ────────────────────────────────────────
koto = song.add_track(Track(name="koto", instrument="koto_ks", volume=0.75, pan=-0.15))

persian = scale("A", "persian", octave=4)

# Exposition — exploring the scale
exposition = humanize(
    [
        Note("A", 4, HALF),
        r(HALF),
        Note("A#", 4, QUARTER),
        Note("C#", 5, QUARTER),
        r(HALF),
        Note("D", 5, HALF),
        Note("D#", 5, QUARTER),
        r(QUARTER),
        Note("D#", 5, QUARTER),
        Note("F", 5, QUARTER),
        r(HALF),
        Note("G#", 5, HALF),
        r(QUARTER),
        Note("A", 5, QUARTER),
        Note("A", 5, WHOLE),
        r(BAR),
    ],
    vel_spread=0.09,
    timing_spread=0.05,
)
koto.extend(exposition)

# Main melody — uses the b5 and aug2nds expressively
main_mel = humanize(
    crescendo(
        [
            Note("A", 4, DOTTED_QUARTER),
            Note("A#", 4, EIGHTH),
            Note("C#", 5, HALF),
            Note("D", 5, QUARTER),
            Note("D#", 5, QUARTER),
            Note("A#", 4, HALF),
            Note("G#", 4, QUARTER),
            Note("A", 4, QUARTER),
            Note("C#", 5, HALF),
            r(HALF),
            Note("F", 5, QUARTER),
            Note("D#", 5, QUARTER),
            Note("D", 5, HALF),
            Note("C#", 5, QUARTER),
            Note("A#", 4, QUARTER),
            Note("G#", 4, HALF),
            Note("A", 4, WHOLE),
        ],
        0.4,
        0.88,
    ),
    vel_spread=0.07,
    timing_spread=0.04,
)
koto.extend(main_mel)
koto.extend(main_mel)

# Outro — fade
koto.extend(decrescendo(humanize(exposition[:8], vel_spread=0.09), 0.7, 0.1))

# ── Sitar KS — countermelody, higher ────────────────────────────────────
sitar = song.add_track(Track(name="sitar", instrument="sitar_ks", volume=0.42, pan=0.3))
sitar.extend([r(BAR)] * 6)
counter = humanize(
    [
        Note("A", 5, HALF),
        r(QUARTER),
        Note("G#", 5, QUARTER),
        Note("F", 5, HALF),
        r(HALF),
        Note("D#", 5, QUARTER),
        Note("D", 5, QUARTER),
        r(HALF),
        Note("C#", 5, WHOLE),
        r(BAR),
        Note("A#", 5, HALF),
        r(QUARTER),
        Note("A", 5, QUARTER),
        Note("G#", 5, WHOLE),
        r(BAR),
    ]
    * 2,
    vel_spread=0.1,
    timing_spread=0.06,
)
sitar.extend(counter)

song.effects = {
    "drone_A": lambda s, sr: lowpass(reverb(s, sr, room_size=0.9, wet=0.55), sr, cutoff_hz=300.0),
    "drone_E": lambda s, sr: lowpass(reverb(s, sr, room_size=0.9, wet=0.5), sr, cutoff_hz=400.0),
    "koto": lambda s, sr: reverb(s, sr, room_size=0.65, damping=0.4, wet=0.22),
    "sitar": lambda s, sr: delay(
        reverb(s, sr, room_size=0.7, wet=0.3), sr, delay_ms=681.0, feedback=0.35, wet=0.25
    ),
}
