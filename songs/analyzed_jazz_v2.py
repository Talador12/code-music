"""Analyzed Jazz v2 - generate a jazz song and run Song.analyze() on it."""

from code_music.theory import generate_full_song

song = generate_full_song("jazz", key="Bb", bpm=160, seed=1959)

# Run the full analysis
analysis = song.analyze()
print(f"  Title: {analysis['info']['title']}")
print(f"  Key: {analysis['harmonic'].get('detected_key', '?')}")
print(f"  Chords: {analysis['harmonic'].get('chord_count', 0)}")
print(f"  Notes: {analysis['melodic'].get('note_count', 0)}")
print(f"  Tracks: {analysis['info']['tracks']}")
if "arrangement" in analysis and "score" in analysis["arrangement"]:
    print(f"  Arrangement score: {analysis['arrangement']['score']}/100")
