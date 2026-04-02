"""Mastered Depths — deep electronic track processed through the mastering pipeline."""

from code_music import Chord, EffectsChain, Note, Song, SoundDesigner, Track, euclid, reverb
from code_music.mastering import master_audio, measure_lufs

sub = (
    SoundDesigner("sub")
    .add_osc("sine", volume=1.0)
    .envelope(attack=0.001, decay=0.4, sustain=0.0, release=0.2)
    .pitch_envelope(start_multiplier=3.0, end_multiplier=1.0, duration=0.03)
    .filter("lowpass", cutoff=150, resonance=0.8)
)

song = Song(title="Mastered Depths", bpm=138, sample_rate=44100)
song.register_instrument("sub", sub)

tr_kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
for _ in range(16):
    tr_kick.add(Note("C", 2, 1.0))

tr_sub = song.add_track(Track(name="sub", instrument="sub", volume=0.6))
tr_sub.extend(euclid(5, 16, "C", 1, 1.0))

tr_pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=-0.1))
tr_pad.add(Chord("C", "min7", 3, duration=8.0))
tr_pad.add(Chord("Ab", "maj7", 3, duration=8.0))

tr_hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3))
for _ in range(32):
    tr_hat.add(Note("F#", 6, 0.5))

song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}

# Master the output
audio = song.render()
print(f"Pre-master: {measure_lufs(audio, 44100):.1f} LUFS")
audio = master_audio(audio, 44100, target_lufs=-14.0, ceiling_db=-1.0)
print(f"Post-master: {measure_lufs(audio, 44100):.1f} LUFS")
