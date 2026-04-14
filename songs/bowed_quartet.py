"""Bowed Quartet - four bowed string voices in a classical arrangement."""

from code_music import Note, Song, SoundDesigner, Track, scale
from code_music.theory import generate_phrase, voice_progression

song = Song(title="Bowed Quartet", bpm=72, sample_rate=44100)

# Register bowed string instruments at different registers
for name, bow_p, bright, cutoff in [
    ("violin1", 0.45, 0.65, 5500),
    ("violin2", 0.4, 0.6, 5000),
    ("viola", 0.5, 0.55, 4000),
    ("cello", 0.55, 0.5, 3500),
]:
    sd = (
        SoundDesigner(name)
        .physical_model("bowed_string", volume=0.85, bow_pressure=bow_p, brightness=bright)
        .envelope(attack=0.1, decay=0.15, sustain=0.8, release=0.5)
        .filter("lowpass", cutoff=cutoff, resonance=0.3)
    )
    song.register_instrument(name, sd)

# Progression
progression = [
    ("G", "min"),
    ("Eb", "maj"),
    ("Bb", "maj"),
    ("F", "dom7"),
    ("G", "min"),
    ("D", "dom7"),
    ("G", "min"),
    ("G", "min"),
]

# Voiced chords for the inner parts
voiced = voice_progression(progression, style="classical", octave=4, duration=4.0)

# Violin 1: melody
v1 = song.add_track(Track(name="violin1", instrument="violin1", volume=0.55, pan=0.3))
phrase = generate_phrase(key="G", cadence="perfect", length=8, include_melody=True, seed=42)
if phrase.get("melody"):
    v1.extend(phrase["melody"])
else:
    v1.extend(scale("G", "minor", octave=5, length=16))

# Violin 2: harmony (voiced chords, top note)
v2 = song.add_track(Track(name="violin2", instrument="violin2", volume=0.45, pan=0.15))
for chord_notes in voiced:
    if chord_notes:
        v2.add(chord_notes[-1] if len(chord_notes) > 1 else chord_notes[0])

# Viola: middle voice
va = song.add_track(Track(name="viola", instrument="viola", volume=0.45, pan=-0.15))
for chord_notes in voiced:
    if chord_notes and len(chord_notes) > 1:
        mid_idx = len(chord_notes) // 2
        va.add(chord_notes[mid_idx])
    elif chord_notes:
        va.add(chord_notes[0])

# Cello: bass notes
vc = song.add_track(Track(name="cello", instrument="cello", volume=0.5, pan=-0.3))
for root, _ in progression:
    vc.add(Note(root, 2, 4.0, velocity=65))
