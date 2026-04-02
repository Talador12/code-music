"""Loudness War — demonstrates the difference between unmixed and mastered audio."""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Pattern,
    Song,
    SoundDesigner,
    Track,
    euclid,
    reverb,
)
from code_music.mastering import measure_lufs, normalize_lufs, stereo_analysis

supersaw = (
    SoundDesigner("supersaw")
    .add_osc("sawtooth", volume=0.3)
    .add_osc("sawtooth", detune_cents=10, volume=0.25)
    .add_osc("sawtooth", detune_cents=-10, volume=0.25)
    .envelope(attack=0.01, decay=0.1, sustain=0.7, release=0.3)
    .filter("lowpass", cutoff=4000, resonance=0.5)
)

song = Song(title="Loudness War", bpm=128, sample_rate=44100)
song.register_instrument("supersaw", supersaw)

tr_lead = song.add_track(Track(name="lead", instrument="supersaw", volume=0.5, pan=0.15))
pat = Pattern("C5 Eb5 G5 Bb5 Ab5 G5 Eb5 C5")
tr_lead.extend(pat.to_notes(0.5))
tr_lead.extend(pat.reverse().to_notes(0.5))

tr_bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
tr_bass.extend(euclid(5, 16, "C", 2, 0.5))

tr_kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
for _ in range(8):
    tr_kick.add(Note("C", 2, 1.0))

tr_pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=-0.1))
tr_pad.add(Chord("C", "min7", 3, duration=8.0))

song.effects = {"lead": EffectsChain().add(reverb, room_size=0.4, wet=0.2)}

audio = song.render()
print(f"Raw: {measure_lufs(audio, 44100):.1f} LUFS")
print(f"Stereo: {stereo_analysis(audio)}")
loud = normalize_lufs(audio, 44100, target_lufs=-14.0)
print(f"Normalized: {measure_lufs(loud, 44100):.1f} LUFS")
