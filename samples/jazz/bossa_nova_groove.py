"""Bossa nova groove - Jobim-style with Rhodes and nylon guitar feel."""

from code_music import (
    Note,
    Chord,
    Track,
    Song,
    EffectsChain,
    scale,
    reverb,
    chorus,
    delay,
    MP,
    P,
    MF,
)
from code_music.theory.rhythm import bossa_nova_pattern, apply_groove, groove_template

song = Song(title="Bossa Nova Groove", bpm=140, key_sig="F", time_sig=(4, 4))

# Chord progression: Girl from Ipanema vibes
prog = [
    ("F", "maj7"),
    ("F", "maj7"),
    ("G", "min7"),
    ("G", "min7"),
    ("G", "min7"),
    ("C", "dom7"),
    ("F", "maj7"),
    ("F", "maj7"),
]

# Rhodes pad with open voicings
pad = song.add_track(Track(name="rhodes", instrument="rhodes", volume=0.45, pan=-0.15))
for root, shape in prog:
    pad.add(Chord(root, shape, 3, duration=4.0, velocity=MP))

# Nylon guitar montuno (use acoustic guitar preset)
guitar = song.add_track(Track(name="guitar", instrument="guitar_acoustic", volume=0.4, pan=0.2))
bossa_groove = groove_template("bossa")
for root, shape in prog:
    notes = scale(root, "major", 4, length=8)
    grooved = apply_groove(notes, bossa_groove, strength=0.8)
    guitar.extend(grooved)

# Bass: root and fifth, bossa feel
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5, pan=0.1))
for root, shape in prog:
    bass.add(Note(root, 2, 2.0, velocity=MF))
    fifth_map = {"maj7": 7, "min7": 7, "dom7": 7}
    from code_music.engine import note_name_to_midi, midi_to_note_name

    root_midi = note_name_to_midi(root, 2)
    fifth_midi = root_midi + fifth_map.get(shape, 7)
    name, oct = midi_to_note_name(fifth_midi)
    bass.add(Note(name, oct, 2.0, velocity=MP))

# Bossa drums
drums_pat = bossa_nova_pattern(bars=8)
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.5))
kick.extend(drums_pat["kick"])
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.3))
snare.extend(drums_pat["snare"])
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.25))
hat.extend(drums_pat["hat"])

# Effects
song.effects = {
    "rhodes": EffectsChain().add(chorus, rate_hz=0.6, wet=0.25).add(reverb, room_size=0.5, wet=0.2),
    "guitar": EffectsChain().add(reverb, room_size=0.3, wet=0.15),
}
