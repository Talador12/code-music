"""Pop Form Demo — a full pop structure from the song_form template."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import progression_from_roman, section_bars, song_form

song = Song(title="Pop Form Demo", bpm=120)

# Get the pop form template
form = song_form("pop")
bars = section_bars("pop", bars_per_section=4)

# Chord progressions per section type
section_chords = {
    "intro": progression_from_roman(["I", "V"], "G"),
    "verse": progression_from_roman(["I", "V", "vi", "IV"], "G"),
    "chorus": progression_from_roman(["IV", "V", "I", "vi"], "G"),
    "bridge": progression_from_roman(["ii", "V", "iii", "vi"], "G"),
    "outro": progression_from_roman(["IV", "V", "I"], "G"),
}

# Build the full progression from the form
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.15))
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for section_name, bar_count in bars:
    chords = section_chords.get(section_name, [("G", "maj")])
    for i in range(bar_count):
        root, shape = chords[i % len(chords)]
        pad.add(Chord(root, shape, 3, duration=4.0))
        bass.add(Note(root, 2, 4.0))

# Simple melody over the whole thing
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=0.15))
from code_music.theory import generate_scale_melody  # noqa: E402

melody = generate_scale_melody("G", "major", length=64, octave=5, contour="arch", seed=42)
lead.extend(melody)

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
    "lead": EffectsChain().add(delay, delay_ms=250, feedback=0.2, wet=0.15),
}
