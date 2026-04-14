"""fill_tracks_demo.py - Demonstrates Song.fill_tracks().

Starts with just a simple melody, then calls fill_tracks(genre="jazz")
to auto-generate bass, chords, and drums. One melody in, full band out.

Style: Jazz (auto-arranged), C major, 120 BPM.
"""

from code_music import Note, Song, Track, scale

song = Song(title="Fill Tracks Demo", bpm=120, sample_rate=44100, key_sig="C")

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5))
melody_notes = scale("C", "major", octave=5, length=8)
for n in melody_notes:
    lead.add(Note(n.pitch, n.octave, 0.5))
for n in reversed(melody_notes):
    lead.add(Note(n.pitch, n.octave, 0.5))
lead.extend(scale("C", "pentatonic", octave=5, length=8))

song.fill_tracks(genre="jazz", seed=42)
