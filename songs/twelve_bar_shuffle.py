"""Twelve Bar Shuffle — classic 12-bar blues with walking bass and shuffle drums."""

from code_music import Chord, EffectsChain, Note, Song, Track, distortion, reverb
from code_music.theory import generate_bass_line, generate_drums, twelve_bar_blues

song = Song(title="Twelve Bar Shuffle", bpm=130)

# Generate the blues progression
prog = twelve_bar_blues("E")

# Rhythm guitar — power chords through the 12 bars
rhythm = song.add_track(Track(name="rhythm", instrument="sawtooth", volume=0.4, pan=-0.2))
for root, shape in prog:
    rhythm.add(Chord(root, shape, 3, duration=4.0))

# Walking bass from the progression
bass_chords = [(root, shape) for root, shape in prog]
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55, pan=0.0))
bass_notes = generate_bass_line(bass_chords[:4], style="walking", seed=42)
bass.extend(bass_notes)
bass_notes = generate_bass_line(bass_chords[4:8], style="walking", seed=43)
bass.extend(bass_notes)
bass_notes = generate_bass_line(bass_chords[8:12], style="walking", seed=44)
bass.extend(bass_notes)

# Shuffle drums
drums_data = generate_drums("rock", bars=12)
kick_tr = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.6))
kick_tr.extend(drums_data["kick"])
snare_tr = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.5))
snare_tr.extend(drums_data["snare"])
hat_tr = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3))
hat_tr.extend(drums_data["hat"])

# Blues lick melody
lead = song.add_track(Track(name="lead", instrument="piano", volume=0.45, pan=0.2))
from code_music.theory import blues_lick  # noqa: E402

for _ in range(6):
    lead.extend(blues_lick("E", octave=5, duration=0.5, seed=_))
    lead.add(Note.rest(2.0))

song.effects = {
    "rhythm": EffectsChain().add(distortion, gain=2.5, wet=0.4),
    "lead": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
}
