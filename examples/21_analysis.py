"""Example 21: Analysis — tablature, harmonic analysis, song maps.

Three visualization/analysis tools:
- to_tab(): ASCII guitar/bass tablature from any melodic track
- analyze_harmony(): Roman numeral analysis of chord progressions
- song_map(): ASCII density map showing song structure

Run:
    code-music examples/21_analysis.py --play
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.composition import song_map, to_lead_sheet, to_tab
from code_music.theory import analyze_harmony

song = Song(title="Analysis Demo", bpm=120, sample_rate=22050, key_sig="C")

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4))
for root, shape in [("C", "maj7"), ("A", "min7"), ("F", "maj7"), ("G", "dom7")]:
    pad.add(Chord(root, shape, 3, duration=4.0))

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.2))
for n in ["C", "E", "G", "B", "A", "C", "E", "G", "F", "A", "C", "E", "G", "B", "D", "G"]:
    lead.add(Note(n, 5, 1.0))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root in ["C", "A", "F", "G"]:
    bass.add(Note(root, 2, 4.0))

song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}

# Harmonic analysis
print("=== Harmonic Analysis ===")
analysis = analyze_harmony(song, key="C")
for a in analysis:
    print(
        f"  Beat {a['beat']:.0f}: {a['root']}{a['shape']} → {a['roman']}{a['quality']} ({a['function']})"
    )

# Lead sheet
print(f"\n=== Lead Sheet ===\n{to_lead_sheet(song)}")

# Guitar tab
print(f"=== Guitar Tab ===\n{to_tab(song, tuning='guitar')}")

# Song map
print(f"=== Song Map ===\n{song_map(song)}")
