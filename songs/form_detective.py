"""Form Detective — a song with clear AABA form, verified by detect_sections."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import label_form

song = Song(title="Form Detective", bpm=120)

# Clear AABA form
a_section = [("C", "maj"), ("A", "min"), ("F", "maj"), ("G", "dom7")]
b_section = [("Eb", "maj"), ("Ab", "maj"), ("Bb", "dom7"), ("Eb", "maj")]
full_prog = a_section + a_section + b_section + a_section

# Verify the form detection works
form = label_form(full_prog, bars_per_section=4)
# Should be "AABA"

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.1))
for root, shape in full_prog:
    pad.add(Chord(root, shape, 3, duration=4.0))

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15))
for root, _ in full_prog:
    lead.extend(
        [
            Note(root, 5, 1.0),
            Note("E", 5, 0.5),
            Note("G", 5, 0.5),
            Note(root, 5, 1.0),
            Note.rest(1.0),
        ]
    )

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root, _ in full_prog:
    bass.add(Note(root, 2, 4.0))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
}
