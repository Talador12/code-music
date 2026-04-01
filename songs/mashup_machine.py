"""mashup_machine.py — Showcases Track.concat() + Section.repeat() together.

A genre-shifting mashup that uses concat() to stitch completely different
musical sections together and repeat() to loop the hook. Starts ambient,
goes EDM, drops into jazz, then loops the EDM hook to close.

Style: Genre mashup, various keys, 120 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb, stereo_width

song = Song(title="Mashup Machine", bpm=120)

r = Note.rest

# ── Part 1: Ambient intro (8 bars) ───────────────────────────────────────
ambient_pad = Track(name="pad", instrument="pad", volume=0.35)
for _ in range(8):
    ambient_pad.add(Chord("E", "min7", 3, duration=4.0))

ambient_lead = Track(name="lead", instrument="triangle", volume=0.3)
ambient_melody = [Note("B", 5, 2.0), Note("G", 5, 1.0), Note("E", 5, 1.0)]
for _ in range(8):
    ambient_lead.extend(ambient_melody)

# ── Part 2: EDM drop (8 bars) ────────────────────────────────────────────
edm_pad = Track(name="pad", instrument="pad", volume=0.35)
for _ in range(4):
    edm_pad.extend(
        [
            Chord("A", "min", 3, duration=4.0),
            Chord("F", "maj", 3, duration=4.0),
        ]
    )

edm_lead = Track(name="lead", instrument="sawtooth", volume=0.5)
edm_hook = [
    Note("A", 5, 0.5),
    Note("C", 6, 0.5),
    Note("E", 5, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 1.0),
    Note("F", 5, 1.0),
]
for _ in range(4):
    edm_lead.extend(edm_hook + [r(2.0)])

# ── Part 3: Jazz interlude (8 bars) ──────────────────────────────────────
jazz_pad = Track(name="pad", instrument="organ", volume=0.3)
jazz_chords = [
    Chord("D", "min7", 3, duration=4.0),
    Chord("G", "dom7", 3, duration=4.0),
    Chord("C", "maj7", 3, duration=4.0),
    Chord("A", "dom7", 3, duration=4.0),
]
for _ in range(2):
    jazz_pad.extend(jazz_chords)

jazz_lead = Track(name="lead", instrument="piano", volume=0.45)
jazz_lick = [
    Note("D", 5, 0.5),
    Note("F", 5, 0.5),
    Note("A", 5, 0.5),
    Note("C", 6, 0.5),
    Note("B", 5, 1.0),
    Note("G", 5, 1.0),
    Note("E", 5, 0.5),
    Note("C", 5, 0.5),
    Note("A", 4, 1.0),
    r(1.0),
]
for _ in range(4):
    jazz_lead.extend(jazz_lick)

# ── Concat the parts ─────────────────────────────────────────────────────
song.add_track(
    ambient_pad.fade_in(8.0)
    .concat(edm_pad)
    .concat(jazz_pad)
    .concat(edm_pad)  # reprise
    .concat(ambient_pad.fade_out(8.0))
)
song.add_track(
    ambient_lead.fade_in(8.0)
    .concat(edm_lead)
    .concat(jazz_lead)
    .concat(edm_lead)  # reprise
    .concat(ambient_lead.fade_out(8.0))
)

# ── Drums — enter at EDM, stay for jazz and reprise ──────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.75))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.5))
kick.add(r(32.0))  # silent during ambient intro
snare.add(r(32.0))
for _ in range(24):  # EDM + jazz + EDM reprise
    kick.extend([Note("C", 2, 1.0)] * 4)
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)])
kick.add(r(32.0))  # silent during ambient outro
snare.add(r(32.0))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.6, wet=0.3).add(stereo_width, width=1.5),
    "lead": EffectsChain()
    .add(delay, delay_ms=250, feedback=0.2, wet=0.15)
    .add(reverb, room_size=0.4, wet=0.15),
}
