# For Creators

You want to make music. You don't need to know music theory.
You need Python 3.11+. That's all.

## Setup

```bash
git clone https://github.com/Talador12/code-music
cd code-music
make dev
```

## Your first song in 5 minutes

Copy this into `songs/my_first_song.py` and run it:

```python
from code_music import Song, Track, Note, scale

# 1. Create a song — give it a name and a speed (BPM = beats per minute)
song = Song(title="My First Song", bpm=90)

# 2. Add a track — pick an instrument
melody = song.add_track(Track(name="melody", instrument="piano", volume=0.8))

# 3. Add notes — pitch name, octave number (4 = middle), how long to hold
melody.add(Note("C", 4, duration=1.0))   # C, held for 1 beat
melody.add(Note("E", 4, duration=1.0))   # E
melody.add(Note("G", 4, duration=1.0))   # G
melody.add(Note("C", 5, duration=2.0))   # high C, held for 2 beats
melody.add(Note.rest(1.0))               # silence for 1 beat
melody.add(Note("G", 4, duration=1.0))
melody.add(Note("E", 4, duration=1.0))
melody.add(Note("C", 4, duration=2.0))
```

```bash
make play-my_first_song       # renders and plays immediately

# Or play directly from Python (no file saved):
code-music songs/my_first_song.py --play

# Or from inside a script:
from code_music import play
play(song)
```

## Add a chord (multiple notes at once)

```python
from code_music import Song, Track, Chord

song = Song(title="With Chords", bpm=100)
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.6))

# Chord: root note, chord type, octave, how long
pad.add(Chord("C", "maj", 3, duration=4.0))    # C major, 4 beats
pad.add(Chord("A", "min", 3, duration=4.0))    # A minor
pad.add(Chord("F", "maj", 3, duration=4.0))    # F major
pad.add(Chord("G", "maj", 3, duration=4.0))    # G major
```

## Use a scale (a collection of notes that sound good together)

```python
from code_music import Song, Track, scale

song = Song(title="Scale Demo", bpm=120)
tr = song.add_track(Track(instrument="piano"))

# Get all notes of a scale
notes = scale("C", "major", octave=4)  # C D E F G A B C
tr.extend(notes)                        # add them all at once
```

You don't need to know what "major" means — just try different ones and
listen. Common choices:

| Name | Sounds like |
|---|---|
| `"major"` | Happy, bright, familiar |
| `"minor"` | Sad, dark, emotional |
| `"pentatonic"` | Simple, no wrong notes, guitar solos |
| `"blues"` | Soulful, tension |
| `"dorian"` | Minor but warmer |
| `"lydian"` | Dreamy, floating |

## Add drums

```python
from code_music import Song, Track, Note

song = Song(title="With Drums", bpm=120)

kick  = song.add_track(Track(instrument="drums_kick",  volume=1.0))
snare = song.add_track(Track(instrument="drums_snare", volume=0.8))
hat   = song.add_track(Track(instrument="drums_hat",   volume=0.5))

r = Note.rest  # shortcut for silence

# 4 bars of standard beat: kick on 1&3, snare on 2&4, hat on every 8th
for _ in range(4):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])
    hat.extend([Note("F", 5, 0.5)] * 8)
```

## Use note duration helpers (no math required)

```python
from code_music import WHOLE, HALF, QUARTER, EIGHTH, SIXTEENTH

# Instead of remembering 4.0 = whole note, 0.5 = eighth note:
note = Note("C", 4, QUARTER)    # one beat
note = Note("G", 4, HALF)       # two beats
note = Note("E", 4, DOTTED_QUARTER)  # one and a half beats
```

## Add reverb to make it sound bigger

```python
from code_music import Song, Track, Note, reverb

song = Song(title="With Reverb", bpm=90)
piano = song.add_track(Track(name="piano", instrument="piano"))
piano.add(Note("C", 4, 4.0))

# Apply reverb to the piano track when rendering
song._effects = {
    "piano": lambda s, sr: reverb(s, sr, room_size=0.7, wet=0.3)
}
```

## Add voice with one-line pacing presets

```python
from code_music import Song, VoiceClip, VoiceTrack

song = Song(title="Voice Presets", bpm=96)
vox = song.add_voice_track(VoiceTrack(name="vox"))

vox.add(VoiceClip.narration("welcome to code music", voice="Samantha", backend="say"), beat_offset=0.0)
vox.add(VoiceClip.rap("welcome to code music", voice="Zarvox", backend="say"), beat_offset=8.0)
```

Want a ready-made example? Start from `samples/voices/voice_pacing_demo.py`.

## Steal from an existing song

The simplest way to learn: open any file in `songs/` and modify it.
Change the BPM, change a chord, add a note. Everything is labelled.

```bash
cp songs/lo_fi_loop.py songs/my_lofi.py
# edit my_lofi.py, then:
make play-my_lofi
```

## Song templates

Start from a template in `songs/`:

| Template style | File to copy |
|---|---|
| Lo-fi hip-hop | `lo_fi_loop.py` |
| Trance / EDM | `trance_odyssey.py` |
| Ambient / chill | `deep_space_drift.py` |
| Jazz | `tank_bebop.py` |
| Orchestral | `cinematic_rise.py` |

## Export your song

```bash
code-music songs/my_first_song.py --flac    # Spotify-quality lossless
code-music songs/my_first_song.py --mp3     # 320kbps for sharing
code-music songs/my_first_song.py --watch   # re-renders every time you save
```

## The main instruments

Pick any of these for `instrument=` in your `Track`:

```
piano         organ         guitar_acoustic   guitar_electric
violin        cello         strings           flute
saxophone     trumpet       trombone          french_horn
pad           supersaw      bass              pluck
drums_kick    drums_snare   drums_hat         drums_808
choir_aah     choir_ooh     vibraphone        marimba
```

## Chord types

```
"maj"    "min"    "dom7"   "maj7"   "min7"
"sus2"   "sus4"   "dim"    "aug"    "9"
```

---

*Ready to go deeper? → [For Theory Heads](for_theory_heads.md)*
*Want to extend the engine? → [For Developers](for_developers.md)*
