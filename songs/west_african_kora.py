"""West African Kora - pentatonic plucked kora with djembe rhythm."""

from code_music import Note, Song, Track, scale

song = Song(title="West African Kora", bpm=105, sample_rate=44100)

kora = song.add_track(Track(name="kora", instrument="pluck", volume=0.5, pan=0.1))
kora.extend(scale("D", "pentatonic", octave=5, length=16))
kora.extend(scale("D", "pentatonic", octave=4, length=16))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.45))
for root in ["D", "G", "A", "D"] * 4:
    bass.add(Note(root, 2, 2.0, velocity=60))

djembe = song.add_track(Track(name="djembe", instrument="drums_kick", volume=0.6))
pattern = [1, 0, 1, 0, 0, 1, 0, 1]
for _ in range(4):
    for hit in pattern:
        if hit:
            djembe.add(Note("C", 4, 0.5, velocity=70))
        else:
            djembe.add(Note.rest(0.5))
