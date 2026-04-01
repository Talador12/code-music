"""08 — Live coding: instant feedback with --watch --play.

Usage:
    code-music examples/08_live_coding.py --watch --play

This starts a file watcher. Every time you save this file, it
re-renders and plays automatically. Edit the notes below and save
to hear changes immediately — no manual steps needed.

Try changing:
- The BPM (line 18)
- The chord progression (line 24)
- The melody notes (line 30)
- The instrument (line 21)
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb

song = Song(title="Live Coding Playground", bpm=120)  # Try: 80, 140, 160

# Pad — change the chords to hear different harmonies
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4))  # Try: organ
pad.extend(
    [
        Chord("C", "maj7", 3, duration=4.0),  # Try: A min7
        Chord("A", "min7", 3, duration=4.0),  # Try: F maj7
        Chord("F", "maj7", 3, duration=4.0),  # Try: D min7
        Chord("G", "dom7", 3, duration=4.0),  # Try: E dom7
    ]
)

# Lead — change the melody
lead = song.add_track(Track(name="lead", instrument="piano", volume=0.55))  # Try: sawtooth
lead.extend(
    [
        Note("E", 5, 0.5),
        Note("G", 5, 0.5),
        Note("C", 5, 1.0),  # Try different pitches
        Note("D", 5, 0.5),
        Note("F", 5, 0.5),
        Note("A", 4, 1.0),
        Note("C", 5, 0.5),
        Note("E", 5, 0.5),
        Note("G", 5, 1.0),
        Note("F", 5, 0.5),
        Note("D", 5, 0.5),
        Note("C", 5, 1.0),
        Note("E", 5, 2.0),
        Note.rest(2.0),
        Note("G", 5, 1.0),
        Note("E", 5, 1.0),
        Note("C", 5, 2.0),
    ]
)

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55))
bass.extend([Note("C", 2, 4.0), Note("A", 2, 4.0), Note("F", 2, 4.0), Note("G", 2, 4.0)])

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
    "lead": EffectsChain().add(reverb, room_size=0.4, wet=0.15),
}
