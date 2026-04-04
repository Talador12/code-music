"""Serial Composition — 12-tone row and its four transforms as melody."""

from code_music import EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import row_transforms, tone_row

song = Song(title="Serial Composition", bpm=72)

_NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

row = tone_row(seed=42)
transforms = row_transforms(row)

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.1))
for label in ["prime", "inversion", "retrograde", "retrograde_inversion"]:
    for pc in transforms[label]:
        lead.add(Note(_NOTE_NAMES[pc], 5, 1.0))
    lead.add(Note.rest(2.0))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.4))
for pc in transforms["prime"]:
    bass.add(Note(_NOTE_NAMES[pc], 3, 4.0))

song.effects = {
    "lead": EffectsChain().add(delay, delay_ms=400, feedback=0.2, wet=0.2),
    "bass": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
}
