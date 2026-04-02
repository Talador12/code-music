"""Example 13: Granular Synthesis and Physical Modeling.

Two advanced synthesis techniques:
- Granular: scatter tiny grains of sound for clouds, textures, and atmospheres
- Physical modeling: simulate real instruments with waveguides and resonators

Run:
    code-music examples/13_granular_and_physical.py --play
"""

from code_music import (
    EffectsChain,
    Note,
    Song,
    SoundDesigner,
    Track,
    reverb,
)

# ---------------------------------------------------------------------------
# Granular synthesis — clouds of tiny sound grains
# ---------------------------------------------------------------------------

cloud = (
    SoundDesigner("cloud")
    .add_osc("sine", volume=0.3)
    .granular(grain_size=0.06, density=20, scatter=0.7, volume=0.7, seed=42)
    .envelope(attack=0.5, decay=0.3, sustain=0.4, release=1.0)
    .filter("lowpass", cutoff=3000, resonance=0.4)
)

# ---------------------------------------------------------------------------
# Physical modeling — simulate real instruments
# ---------------------------------------------------------------------------

# Karplus-Strong plucked string (guitar-like)
guitar = (
    SoundDesigner("guitar")
    .physical_model("karplus_strong", volume=0.9, decay=0.998, brightness=0.5)
    .envelope(attack=0.001, decay=0.5, sustain=0.1, release=0.3)
)

# Waveguide pipe (flute-like)
flute = (
    SoundDesigner("flute")
    .physical_model("waveguide_pipe", volume=0.8, feedback=0.97, brightness=0.65)
    .envelope(attack=0.05, decay=0.1, sustain=0.7, release=0.3)
    .filter("lowpass", cutoff=4000, resonance=0.3)
)

# Modal synthesis (struck metal)
gong = (
    SoundDesigner("gong")
    .physical_model("modal", volume=0.9)
    .envelope(attack=0.001, decay=1.5, sustain=0.1, release=1.0)
)

# ---------------------------------------------------------------------------
# Build a song combining both techniques
# ---------------------------------------------------------------------------

song = Song(title="Granular & Physical", bpm=80, sample_rate=22050)

for name, designer in [("cloud", cloud), ("guitar", guitar), ("flute", flute), ("gong", gong)]:
    song.register_instrument(name, designer)

# Granular cloud bed
tr_cloud = song.add_track(Track(name="cloud", instrument="cloud", volume=0.3))
tr_cloud.add(Note("C", 4, 16.0))

# Guitar arpeggios
tr_guitar = song.add_track(Track(name="guitar", instrument="guitar", volume=0.5))
for note in ["C", "E", "G", "C", "G", "E", "C", "B"]:
    tr_guitar.add(Note(note, 4, 2.0))

# Flute melody
tr_flute = song.add_track(Track(name="flute", instrument="flute", volume=0.45, pan=0.2))
flute_melody = [
    ("E", 5, 2.0),
    ("G", 5, 1.5),
    ("A", 5, 2.5),
    ("G", 5, 2.0),
    ("E", 5, 1.0),
    ("D", 5, 2.0),
    ("C", 5, 3.0),
    ("E", 5, 2.0),
]
for note_name, oct, dur in flute_melody:
    tr_flute.add(Note(note_name, oct, dur))

# Gong accents
tr_gong = song.add_track(Track(name="gong", instrument="gong", volume=0.25, pan=-0.2))
tr_gong.add(Note("C", 3, 4.0))
tr_gong.add(Note.rest(4.0))
tr_gong.add(Note("G", 3, 4.0))
tr_gong.add(Note.rest(4.0))

song.effects = {
    "cloud": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
    "flute": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
    "gong": EffectsChain().add(reverb, room_size=0.85, wet=0.4),
}
