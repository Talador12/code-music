"""10 — Music analysis: detect the key of any song.

Run:  code-music examples/10_analysis.py --play
"""

from code_music import Chord, Note, Song, Track, detect_key, generate_song

# Create a song in G major
song = Song(title="Key Detection Demo", bpm=120, sample_rate=22050)

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4))
pad.add(Chord("G", "maj", 3, duration=4.0))
pad.add(Chord("C", "maj", 3, duration=4.0))
pad.add(Chord("D", "maj", 3, duration=4.0))
pad.add(Chord("G", "maj", 3, duration=4.0))

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.6))
for note in ["G", "A", "B", "D", "E", "D", "B", "G"]:
    lead.add(Note(note, 5, 1.0))

# Detect the key
root, mode, confidence = detect_key(song)
print(f"Detected key: {root} {mode} ({confidence:.0%} confidence)")

# Works on generated songs too:
jazz = generate_song("jazz", bars=8, seed=42)
r, m, c = detect_key(jazz)
print(f"Jazz song key: {r} {m} ({c:.0%})")

# detect_key uses Krumhansl-Kessler pitch-class profile correlation.
# It counts how often each pitch appears (weighted by duration),
# then correlates against known major/minor key profiles.
