"""persian_nights.py — Middle Eastern fusion. Bb Phrygian dominant, 105 BPM.

Uses Track.loop for the hypnotic oud ostinato, Track.transpose for the
modulating bridge, and Track.stretch for the rubato outro.

Style: Middle Eastern fusion, Bb Phrygian dominant, 105 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb

song = Song(title="Persian Nights", bpm=105)

r = Note.rest

# ── Oud ostinato — one bar, looped ───────────────────────────────────────
oud_bar = Track(name="oud", instrument="pluck", volume=0.5, pan=0.2)
oud_bar.extend(
    [
        Note("Bb", 4, 0.5),
        Note("Cb", 5, 0.5),
        Note("D", 5, 0.5),
        Note("Eb", 5, 0.5),
        Note("D", 5, 0.5),
        Note("Cb", 5, 0.5),
        Note("Bb", 4, 0.5),
        r(0.5),
    ]
)
song.add_track(oud_bar.loop(16))

# ── Darbuka — frame drum pattern, looped ─────────────────────────────────
darbuka_bar = Track(name="darbuka", instrument="drums_kick", volume=0.6)
darbuka_bar.extend(
    [
        Note("C", 2, 0.5),
        r(0.25),
        Note("C", 2, 0.25),
        Note("C", 2, 0.5),
        r(0.5),
        Note("C", 2, 0.25),
        Note("C", 2, 0.25),
        r(0.5),
        Note("C", 2, 0.5),
        r(0.5),
    ]
)
song.add_track(darbuka_bar.loop(16))

# ── Bass drone ───────────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for _ in range(16):
    bass.extend([Note("Bb", 2, 4.0)])

# ── Lead — melody + transposed bridge + stretched outro ──────────────────
lead_theme = Track(name="lead", instrument="sawtooth", volume=0.45, pan=-0.15)
phrase = [
    Note("Bb", 5, 0.5),
    Note("Cb", 6, 0.5),
    Note("D", 6, 1.0),
    Note("Eb", 6, 0.5),
    Note("D", 6, 0.5),
    Note("Cb", 6, 0.5),
    Note("Bb", 5, 0.5),
    Note("Ab", 5, 1.0),
    Note("Bb", 5, 1.0),
    r(2.0),
]
for _ in range(3):
    lead_theme.extend(phrase)

# Main: theme x2, bridge (up 5), theme stretched for outro
main = lead_theme.loop(2)
bridge = lead_theme.transpose(5)
outro = lead_theme.stretch(1.5).fade_out(beats=16.0)
song.add_track(main.concat(bridge).concat(outro))

# ── Pad ──────────────────────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.2))
for _ in range(16):
    pad.add(Chord("Bb", "min", 3, duration=4.0))

song.effects = {
    "oud": EffectsChain().add(delay, delay_ms=285, feedback=0.2, wet=0.15),
    "lead": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
}
