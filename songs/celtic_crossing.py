"""celtic_crossing.py — Celtic/Irish trad. D Mixolydian, 132 BPM. Jig feel.

A lively Irish jig in 6/8 time with a fiddle-like lead, bodhrán rhythm,
and a drone bass. Uses Mixolydian mode for the classic Celtic flavor.

Style: Irish trad, D Mixolydian, 6/8 time, 132 BPM.
"""

from code_music import Chord, Note, Song, Track, reverb

song = Song(title="Celtic Crossing", bpm=132, time_sig=(6, 8))

r = Note.rest
# In 6/8 at 132 BPM (dotted quarter = pulse), each bar = 3 beats
BAR = 3.0

# ── Bodhrán (frame drum) ─────────────────────────────────────────────────
kick = song.add_track(Track(name="bodhran", instrument="drums_kick", volume=0.65))
for _ in range(24):
    kick.extend([Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5), Note("C", 2, 0.5), r(0.5)])

# ── Drone bass — open D string ───────────────────────────────────────────
drone = song.add_track(Track(name="drone", instrument="bass", volume=0.45, pan=-0.15))
for _ in range(24):
    drone.add(Note("D", 2, BAR))

# ── Chords — bouzouki/guitar ─────────────────────────────────────────────
chords = song.add_track(Track(name="bouzouki", instrument="pluck", volume=0.4, pan=-0.2))
prog = [
    Chord("D", "maj", 3, duration=BAR),
    Chord("C", "maj", 3, duration=BAR),
    Chord("G", "maj", 3, duration=BAR),
    Chord("D", "maj", 3, duration=BAR),
]
for _ in range(6):
    chords.extend(prog)

# ── Fiddle — jig melody in D Mixolydian ──────────────────────────────────
fiddle = song.add_track(Track(name="fiddle", instrument="sawtooth", volume=0.55, pan=0.25))

phrase_a = [
    Note("D", 5, 0.5),
    Note("E", 5, 0.5),
    Note("F#", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
]
phrase_b = [
    Note("F#", 5, 0.5),
    Note("D", 5, 0.5),
    Note("E", 5, 0.5),
    Note("C", 5, 0.5),
    Note("D", 5, 0.5),
    Note("A", 4, 0.5),
]
phrase_c = [
    Note("B", 4, 0.5),
    Note("C", 5, 0.5),
    Note("D", 5, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("F#", 5, 0.5),
]
phrase_d = [
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("D", 5, 1.0),
    r(0.5),
]

jig = phrase_a + phrase_b + phrase_c + phrase_d
for _ in range(6):
    fiddle.extend(jig)

song._effects = {
    "fiddle": lambda s, sr: reverb(s, sr, room_size=0.4, wet=0.18),
    "bouzouki": lambda s, sr: reverb(s, sr, room_size=0.3, wet=0.12),
}
