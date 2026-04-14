"""hip_hop_beat.py - 90 BPM trap-style with 808 bass. Dark and heavy."""

from code_music import Chord, EffectsChain, Note, Song, Track, lowpass, reverb

song = Song(title="Hip Hop Beat", bpm=90, sample_rate=44100)

r = Note.rest

# 808 sub bass - Fm, slides and sustains
sub = song.add_track(Track(name="808", instrument="bass", volume=0.9))
bass_pat = [
    Note("F", 1, 2.0, velocity=90),
    r(1.0),
    Note("Ab", 1, 1.0, velocity=85),
    Note("Eb", 1, 2.0, velocity=88),
    r(1.0),
    Note("Db", 1, 1.0, velocity=80),
]
sub.extend(bass_pat * 8)

# Kick - sparse, on 1
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.95))
kick_pat = [Note("C", 2, 0.5, velocity=95), r(3.5)]
kick.extend(kick_pat * 16)

# Snare/clap - beat 3 (half-time feel)
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.8))
snare_pat = [r(2.0), Note("D", 3, 0.5, velocity=90), r(1.5)]
snare.extend(snare_pat * 16)

# Hi-hats - 16th notes with rolls
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.45))
for _ in range(16):
    hat.extend([Note("F", 5, 0.25, velocity=40)] * 16)

# Dark pad - Fm atmosphere
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.25, pan=-0.1))
for root, shape in [("F", "min7"), ("Db", "maj7"), ("Ab", "maj7"), ("Eb", "min7")] * 4:
    pad.add(Chord(root, shape, 3, duration=4.0, velocity=30))

song.effects = {
    "808": lambda s, sr: lowpass(s, sr, cutoff_hz=150.0),
    "pad": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
}
