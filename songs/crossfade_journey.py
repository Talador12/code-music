"""Crossfade Journey - smooth transitions between contrasting clips."""

from code_music import Chord, Clip, Note, Song, Track, scale

song = Song(title="Crossfade Journey", bpm=110, sample_rate=44100)

# Two contrasting melodic ideas
bright_src = Track(name="bright")
bright_src.extend(scale("C", "major", octave=5, length=8))

dark_src = Track(name="dark")
dark_src.extend(scale("C", "pentatonic_minor", octave=4, length=8))

clip_bright = Clip.from_track(bright_src)
clip_dark = Clip.from_track(dark_src)

# Journey: bright -> crossfade -> dark -> crossfade -> bright
transition_1 = clip_bright.crossfade(clip_dark, overlap_beats=3)
transition_2 = clip_dark.crossfade(clip_bright, overlap_beats=3)

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.55, pan=0.1))
lead.extend(clip_bright.loop(2).to_events())
lead.extend(transition_1.to_events())
lead.extend(clip_dark.loop(2).to_events())
lead.extend(transition_2.to_events())
lead.extend(clip_bright.to_events())

# Harmonic backing
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35, pan=-0.15))
progression = [
    ("C", "maj7"),
    ("F", "maj7"),
    ("G", "dom7"),
    ("C", "maj7"),
    ("C", "min7"),
    ("Ab", "maj7"),
    ("Bb", "maj"),
    ("C", "min7"),
    ("C", "maj7"),
    ("F", "maj7"),
]
for root, shape in progression:
    pad.add(Chord(root, shape, 3, duration=4.0, velocity=45))

# Gentle bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root, _ in progression:
    bass.add(Note(root, 2, 4.0, velocity=60))
