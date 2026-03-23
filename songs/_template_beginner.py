"""Beginner song template — read every comment, change one thing at a time.

Copy this file, rename it, and make it yours:
    cp songs/_template_beginner.py songs/my_song.py
    make play-my_song

The only rule: the file must define a variable called `song` at the top level.
"""

from code_music import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    # Duration helpers — so you don't have to remember "4.0 = whole note"
    WHOLE,
    Chord,
    Note,
    Song,
    Track,
    delay,
    # Effects
    reverb,
)

# ── 1. CREATE YOUR SONG ───────────────────────────────────────────────────────
# title = what it's called
# bpm   = speed. 60 = slow walk. 90 = comfortable. 120 = upbeat. 140 = fast.
song = Song(title="My Song", bpm=95)

# ── 2. ADD TRACKS ─────────────────────────────────────────────────────────────
# Each track is one instrument playing its part.
# instrument options: "piano", "guitar_acoustic", "strings", "pad",
#   "saxophone", "trumpet", "flute", "bass", "drums_kick", ...
# volume: 0.0 (silent) → 1.0 (full)

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.45))
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.7))
mel = song.add_track(Track(name="melody", instrument="piano", volume=0.8))

# ── 3. WRITE THE CHORD PROGRESSION ───────────────────────────────────────────
# Chord(root, type, octave, duration)
# root   = note name: "C" "D" "E" "F" "G" "A" "B"  (add # for sharp: "F#")
# type   = "maj" "min" "dom7" "maj7" "min7" "sus2" "sus4"
# octave = 3 or 4 for chords (lower = deeper)
# duration = how many beats to hold it

# This is Am - F - C - G, one of the most common progressions in all of music
chords = [
    Chord("A", "min7", 3, duration=WHOLE),  # 4 beats
    Chord("F", "maj7", 3, duration=WHOLE),
    Chord("C", "maj", 3, duration=WHOLE),
    Chord("G", "dom7", 3, duration=WHOLE),
]
# Repeat the progression twice
for _ in range(2):
    pad.extend(chords)

# ── 4. WRITE THE BASS LINE ────────────────────────────────────────────────────
# Bass plays the root note of each chord, simple and locked
bass_notes = [
    Note("A", 2, WHOLE),  # A, low octave, held for 4 beats
    Note("F", 2, WHOLE),
    Note("C", 3, WHOLE),
    Note("G", 2, WHOLE),
]
for _ in range(2):
    bass.extend(bass_notes)

# ── 5. WRITE THE MELODY ───────────────────────────────────────────────────────
# Notes use the A minor pentatonic scale: A C D E G
# These all sound good over the chords above.
# Try changing the order, the durations, or the octave.
melody = [
    Note("A", 4, QUARTER),
    Note("C", 5, QUARTER),
    Note("E", 5, HALF),
    Note("D", 5, QUARTER),
    Note("C", 5, QUARTER),
    Note("A", 4, HALF),
    Note.rest(HALF),  # silence — space is musical too
    Note("G", 4, QUARTER),
    Note("A", 4, QUARTER),
    Note("C", 5, DOTTED_QUARTER),
    Note("A", 4, EIGHTH),
    Note("G", 4, WHOLE),
]
mel.extend(melody)
# Play it a second time
mel.extend(melody)

# ── 6. ADD EFFECTS ────────────────────────────────────────────────────────────
# Effects make things sound bigger and more interesting.
# wet = how much effect (0.0 = dry, 1.0 = fully wet)
# Try increasing or decreasing wet, or commenting these out.
song._effects = {
    "pad": lambda s, sr: reverb(s, sr, room_size=0.7, wet=0.35),
    "melody": lambda s, sr: delay(s, sr, delay_ms=375.0, feedback=0.3, wet=0.2),
}

# ── WHAT TO TRY NEXT ──────────────────────────────────────────────────────────
# 1. Change the BPM above and re-run
# 2. Swap "min7" to "min" on the A chord — hear the difference?
# 3. Add a drums track (copy from songs/lo_fi_loop.py)
# 4. Change the melody notes to something else — any of A C D E G will work
# 5. Try instrument="saxophone" or "guitar_acoustic" on the melody track
# 6. Add a second melody track an octave higher (octave=5) at lower volume
