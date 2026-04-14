"""Example 18: Song Structure - forms, arrangement, sessions, clips.

Demonstrates:
- generate_form(): complete formal structures (sonata, rondo, AABA, etc.)
- suggest_arrangement(): detect section boundaries from analysis
- Session: Ableton-style clip grid with scenes
- Clip: loopable track slices with loop/reverse/crossfade
- Song.fill_tracks(): auto-fill missing instruments
- Song.analyze(): comprehensive analysis in one call
"""

from code_music import (
    Chord,
    Clip,
    Note,
    Session,
    Song,
    Track,
    scale,
    suggest_arrangement,
)
from code_music.theory import generate_form

# --- 1. Generate a complete sonata form ---
print("1. Sonata form generation")
sonata = generate_form("sonata", key="C", bpm=120, seed=42)
print(f"   '{sonata.title}': {len(sonata.tracks)} tracks, {sonata.total_beats:.0f} beats")

# --- 2. Suggest arrangement boundaries ---
print("\n2. Arrangement suggestion")
sections = suggest_arrangement(sonata)
for s in sections[:5]:
    print(
        f"   {s['label']:>8}: bars {s['start_beat']:.0f}-{s['end_beat']:.0f} "
        f"({s['bars']} bars, confidence {s['confidence']:.0%})"
    )
if len(sections) > 5:
    print(f"   ... and {len(sections) - 5} more sections")

# --- 3. Session view: build a song from clips ---
print("\n3. Session view (Ableton-style)")
session = Session(bpm=120, sample_rate=22050)
session.add_track("drums", instrument="drums_kick", volume=0.8)
session.add_track("bass", instrument="bass", volume=0.6)
session.add_track("keys", instrument="piano", volume=0.5)

# Build clips
kick_pat = Track()
for _ in range(4):
    kick_pat.add(Note("C", 4, 1.0, velocity=80))
    kick_pat.add(Note.rest(1.0))

bass_pat = Track()
for root in ["C", "F", "G", "C"]:
    bass_pat.add(Note(root, 2, 2.0, velocity=65))

keys_pat = Track()
for root, shape in [("C", "maj7"), ("F", "maj"), ("G", "dom7"), ("C", "maj")]:
    keys_pat.add(Chord(root, shape, 4, duration=2.0, velocity=50))

# Place clips in the grid
session.set_clip("drums", 0, Clip.from_track(kick_pat))
session.set_clip("bass", 0, Clip.from_track(bass_pat))
session.set_clip("keys", 0, Clip.from_track(keys_pat))

# Render: scene 0 repeated 4 times
song = session.render(scene_order=[0, 0, 0, 0], loops_per_scene=1)
print(f"   Session: {session}")
print(f"   Rendered: '{song.title}', {len(song.tracks)} tracks")

# --- 4. Clip operations ---
print("\n4. Clip operations")
clip = Clip.from_track(kick_pat)
print(f"   Original:    {clip}")
print(f"   Looped 3x:   {clip.loop(3)}")
print(f"   Reversed:    {clip.reverse()}")
print(f"   Trimmed:     {clip.trim(0, 4)}")
print(f"   Quantized:   {clip.quantize_to_bars(beats_per_bar=4)}")

# Crossfade between two clips
clip_a = Clip.from_track(bass_pat)
clip_b = Clip.from_track(keys_pat)
xf = clip_a.crossfade(clip_b, overlap_beats=2)
print(f"   Crossfaded:  {xf}")

# --- 5. Fill tracks (auto-arrangement) ---
print("\n5. Song.fill_tracks()")
sketch = Song(title="Sketch", bpm=120, key_sig="C", sample_rate=22050)
lead = sketch.add_track(Track(name="lead", instrument="sawtooth"))
lead.extend(scale("C", "pentatonic", octave=5, length=16))
print(f"   Before: {len(sketch.tracks)} tracks")
sketch.fill_tracks(genre="jazz", seed=42)
print(f"   After:  {len(sketch.tracks)} tracks ({', '.join(t.name for t in sketch.tracks)})")

# --- 6. Song.analyze() ---
print("\n6. Song.analyze()")
analysis = sketch.analyze()
print(f"   Key: {analysis['harmonic'].get('detected_key', '?')}")
print(f"   Chords: {analysis['harmonic'].get('chord_count', 0)}")
print(f"   Notes: {analysis['melodic'].get('note_count', 0)}")
print(f"   Tracks: {analysis['info']['tracks']}")
if "arrangement" in analysis and "score" in analysis["arrangement"]:
    print(f"   Arrangement score: {analysis['arrangement']['score']}/100")
