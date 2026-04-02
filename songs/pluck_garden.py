"""Pluck Garden — Karplus-Strong strings and waveguide pipes in a chamber setting."""

from code_music import EffectsChain, Note, Pattern, Song, SoundDesigner, Track, reverb

harp = (
    SoundDesigner("harp")
    .physical_model("karplus_strong", volume=0.9, decay=0.999, brightness=0.6)
    .envelope(attack=0.001, decay=0.8, sustain=0.05, release=0.5)
)
flute = (
    SoundDesigner("flute")
    .physical_model("waveguide_pipe", volume=0.8, feedback=0.97, brightness=0.7)
    .envelope(attack=0.04, decay=0.1, sustain=0.7, release=0.3)
    .filter("lowpass", cutoff=5000, resonance=0.3)
)
chime = (
    SoundDesigner("chime")
    .physical_model("modal", volume=0.7)
    .envelope(attack=0.001, decay=1.0, sustain=0.0, release=0.6)
)

song = Song(title="Pluck Garden", bpm=72, sample_rate=44100)
for name, d in [("harp", harp), ("flute", flute), ("chime", chime)]:
    song.register_instrument(name, d)

# Harp arpeggios from Pattern
harp_pat = Pattern("C4 E4 G4 C5 G4 E4 D4 G4 B4 D5 B4 G4 C4 F4 A4 C5")
tr_h = song.add_track(Track(name="harp", instrument="harp", volume=0.5))
tr_h.extend(harp_pat.to_notes(0.75))

# Flute melody
tr_f = song.add_track(Track(name="flute", instrument="flute", volume=0.4, pan=0.15))
flute_mel = [
    ("E", 5, 2.0),
    ("G", 5, 1.5),
    ("A", 5, 2.5),
    ("G", 5, 1.5),
    ("E", 5, 1.0),
    ("D", 5, 1.5),
    ("C", 5, 2.0),
]
for n, o, d in flute_mel:
    tr_f.add(Note(n, o, d))

# Chime accents
tr_c = song.add_track(Track(name="chime", instrument="chime", volume=0.2, pan=-0.2))
tr_c.add(Note("C", 6, 3.0))
tr_c.add(Note.rest(3.0))
tr_c.add(Note("G", 6, 3.0))
tr_c.add(Note.rest(3.0))

song.effects = {
    "harp": EffectsChain().add(reverb, room_size=0.6, wet=0.25),
    "flute": EffectsChain().add(reverb, room_size=0.7, wet=0.3),
    "chime": EffectsChain().add(reverb, room_size=0.85, wet=0.4),
}
