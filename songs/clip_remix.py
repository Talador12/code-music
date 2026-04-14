"""Clip Remix - build a song from reversed and crossfaded clips."""

from code_music import Chord, Clip, Note, Song, Track, scale

song = Song(title="Clip Remix", bpm=128, sample_rate=44100)

# Build a melodic pattern
mel_source = Track(name="lead", instrument="sawtooth")
mel_source.extend(scale("D", "pentatonic_minor", octave=5, length=16))

# Extract clips, manipulate, and reassemble
clip_a = Clip.from_track(mel_source, 0, 8)
clip_b = Clip.from_track(mel_source, 8, 16)
clip_b_rev = clip_b.reverse()

# Crossfade between forward and reversed clips
transition = clip_a.crossfade(clip_b_rev, overlap_beats=2)

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=0.2))
lead.extend(transition.to_events())
lead.extend(clip_b.loop(2).to_events())

# Bass follows root motion
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
for root in ["D", "D", "G", "A"] * 3:
    bass.add(Note(root, 2, 2.0, velocity=65))

# Pad
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35, pan=-0.15))
for root, shape in [("D", "min7"), ("G", "min7"), ("A", "min7"), ("D", "min7")] * 3:
    pad.add(Chord(root, shape, 3, duration=2.0, velocity=45))

# Drums from a clip loop
kick_src = Track()
kick_src.extend([Note("C", 4, 1.0, velocity=80), Note.rest(1.0)] * 2)
kick_clip = Clip.from_track(kick_src)

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
kick.extend(kick_clip.loop(6).to_events())
