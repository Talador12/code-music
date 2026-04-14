"""Japanese Garden - In-Sen scale with sparse, contemplative arrangement."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale

song = Song(title="Japanese Garden", bpm=55, sample_rate=44100)

lead = song.add_track(Track(name="koto", instrument="pluck", volume=0.5, pan=0.1))
notes = scale("D", "in_sen", octave=5, length=10)
for n in notes:
    lead.add(n)
    lead.add(Note.rest(1.0))  # space between notes

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.2, pan=-0.1))
pad.add(Chord("D", "sus2", 3, duration=20.0, velocity=25))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.3))
bass.add(Note("D", 2, 20.0, velocity=40))

song.effects = {
    "koto": EffectsChain().add(reverb, room_size=0.9, wet=0.45),
    "pad": EffectsChain().add(reverb, room_size=0.95, wet=0.5),
}
