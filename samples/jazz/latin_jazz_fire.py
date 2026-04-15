"""Latin jazz fire - Tito Puente meets Chucho Valdes. Clave-locked montuno madness."""

from code_music import (
    Note,
    Chord,
    Track,
    Song,
    EffectsChain,
    reverb,
    delay,
    compress,
    F,
    MF,
    MP,
)
from code_music.theory.rhythm import (
    clave_pattern,
    cascara_pattern,
    montuno_pattern,
    apply_groove,
    groove_template,
)

song = Song(title="Latin Jazz Fire", bpm=180, key_sig="D", time_sig=(4, 4))

# Progression: minor Latin with altered dominants
prog = [
    ("D", "min7"),
    ("D", "min7"),
    ("G", "dom7"),
    ("G", "dom7"),
    ("C", "maj7"),
    ("C", "maj7"),
    ("A", "dom7"),
    ("A", "dom7"),
]

# Clave: the law. Son clave 2-3.
clave = song.add_track(Track(name="clave", instrument="woodblock", volume=0.5, pan=0.1))
clave.extend(clave_pattern("son_23", "C", 5, bars=8))

# Cascara on timbales shell
cascara = song.add_track(Track(name="cascara", instrument="timbales", volume=0.45, pan=-0.1))
cascara.extend(cascara_pattern("cascara_23", "D", 5, bars=8))

# Piano montuno - locked to the clave
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.55, pan=0.2))
for root, shape in prog:
    piano.extend(montuno_pattern(root, shape, octave=4, bars=1))

# Bass: tumbao
from code_music.theory import bass_line_latin

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6, pan=0.0))
bass.extend(bass_line_latin(prog, octave=2))

# Trumpet lead - fire melody
trumpet = song.add_track(Track(name="trumpet", instrument="trumpet", volume=0.6, pan=-0.2))
melody = [
    Note("D", 5, 0.5, F),
    Note("F", 5, 0.5, F),
    Note("A", 5, 0.5, F),
    Note("G", 5, 1.0, MF),
    Note.rest(0.5),
    Note("F", 5, 0.5, F),
    Note("E", 5, 0.5, MF),
    Note("D", 5, 1.0, F),
    Note.rest(0.5),
    Note("A", 5, 0.5, F),
    Note("G", 5, 0.5, MF),
    Note("F", 5, 0.5, MF),
    Note("E", 5, 0.5, F),
    Note("D", 5, 1.5, F),
]
trumpet.extend(melody * 4)

# Congas
congas = song.add_track(Track(name="congas", instrument="conga", volume=0.45, pan=-0.15))
salsa_groove = groove_template("salsa")
conga_notes = [Note("C", 3, 0.25, velocity=0.6)] * (16 * 8)
congas.extend(apply_groove(conga_notes, salsa_groove, strength=0.7))

# Kick drum
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.5))
from code_music import euclid

kick.extend(euclid(3, 8, "C", 2, 0.5) * 8)  # tresillo

song.effects = {
    "trumpet": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
    "piano": EffectsChain().add(compress, threshold=0.5, ratio=3.0),
}
