"""Modal Resonance — struck metal and resonant bodies through physical modeling."""

from code_music import EffectsChain, Note, Song, SoundDesigner, Track, euclid, reverb

bar = (
    SoundDesigner("bar")
    .physical_model("modal", volume=0.9)
    .envelope(attack=0.001, decay=1.2, sustain=0.05, release=0.8)
    .filter("lowpass", cutoff=8000, resonance=0.4)
)
ks_bass = (
    SoundDesigner("ks_bass")
    .physical_model("karplus_strong", volume=0.8, decay=0.995, brightness=0.3)
    .envelope(attack=0.001, decay=0.4, sustain=0.2, release=0.2)
    .filter("lowpass", cutoff=400, resonance=0.8)
)
pipe = (
    SoundDesigner("pipe")
    .physical_model("waveguide_pipe", volume=0.7, feedback=0.96, brightness=0.5)
    .envelope(attack=0.06, decay=0.1, sustain=0.6, release=0.4)
)

song = Song(title="Modal Resonance", bpm=90, sample_rate=44100)
for name, d in [("bar", bar), ("ks_bass", ks_bass), ("pipe", pipe)]:
    song.register_instrument(name, d)

# Struck bar melody
tr_bar = song.add_track(Track(name="bar", instrument="bar", volume=0.4))
melody = [
    ("C", 5),
    ("Eb", 5),
    ("G", 5),
    ("Bb", 5),
    ("Ab", 5),
    ("G", 5),
    ("Eb", 5),
    ("C", 5),
    ("Bb", 4),
    ("G", 4),
    ("Ab", 4),
    ("Bb", 4),
    ("C", 5),
    ("Eb", 5),
    ("F", 5),
    ("G", 5),
]
for n, o in melody:
    tr_bar.add(Note(n, o, 1.0))

# KS bass: euclidean
tr_bass = song.add_track(Track(name="bass", instrument="ks_bass", volume=0.5))
for root in ["C", "Ab", "Eb", "Bb"]:
    tr_bass.extend(euclid(3, 8, root, 2, 0.5))

# Pipe pad
tr_pipe = song.add_track(Track(name="pipe", instrument="pipe", volume=0.35, pan=0.15))
tr_pipe.add(Note("C", 4, 4.0))
tr_pipe.add(Note("Eb", 4, 4.0))
tr_pipe.add(Note("Ab", 4, 4.0))
tr_pipe.add(Note("Bb", 4, 4.0))

song.effects = {
    "bar": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
    "pipe": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
}
