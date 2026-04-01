"""time_warp.py — Showcases Track.stretch() for time manipulation.

A theme is played at normal speed, then at half speed (stretch 2x),
then at double speed (stretch 0.5x), creating a progressive zoom effect.

Style: Experimental electronic, Dm, 120 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb

song = Song(title="Time Warp", bpm=120)

r = Note.rest

# ── Base theme — 4 bars ──────────────────────────────────────────────────
theme = Track(name="lead", instrument="sawtooth", volume=0.5)
melody = [
    Note("D", 5, 0.5),
    Note("F", 5, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("F", 5, 1.0),
    Note("D", 5, 1.0),
    Note("C", 5, 0.5),
    Note("D", 5, 0.5),
    Note("F", 5, 1.0),
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 1.0),
]
for _ in range(2):
    theme.extend(melody)

# Normal → slow → fast → normal
normal = theme.loop(1)
slow = theme.stretch(2.0)
fast = theme.stretch(0.5)
song.add_track(normal.concat(slow).concat(fast).concat(normal))

# ── Bass follows the same stretch pattern ────────────────────────────────
bass_theme = Track(name="bass", instrument="bass", volume=0.6)
bass_notes = [Note("D", 2, 2.0), Note("A", 2, 2.0), Note("Bb", 2, 2.0), Note("C", 3, 2.0)]
for _ in range(2):
    bass_theme.extend(bass_notes)

song.add_track(
    bass_theme.concat(bass_theme.stretch(2.0)).concat(bass_theme.stretch(0.5)).concat(bass_theme)
)

# ── Pad — constant wash ─────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3))
total_beats = normal.total_beats + slow.total_beats + fast.total_beats + normal.total_beats
bars = int(total_beats / 4)
for _ in range(bars):
    pad.add(Chord("D", "min7", 3, duration=4.0))

# ── Drums — simple pulse ────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
for _ in range(bars):
    kick.extend([Note("C", 2, 1.0)] * 4)

song.effects = {
    "lead": EffectsChain()
    .add(delay, delay_ms=250, feedback=0.2, wet=0.15)
    .add(reverb, room_size=0.4, wet=0.15),
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
}
