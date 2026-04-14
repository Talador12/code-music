"""progressive_rock.py - Odd time signature prog rock in 7/8. Yes meets Rush."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb

song = Song(title="Progressive Rock", bpm=144, time_sig=(7, 8), sample_rate=44100)

r = Note.rest
BAR = 3.5  # 7/8 time: 7 eighth notes = 3.5 quarter note beats

# Bass - driving root pattern in 7/8
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
bass_pat = [
    Note("E", 2, 0.5),
    Note("E", 2, 0.5),
    Note("G", 2, 0.5),
    Note("A", 2, 0.5),
    Note("B", 2, 0.5),
    Note("E", 2, 0.5),
    Note("D", 3, 0.5),
]
bass.extend(bass_pat * 24)

# Power chords - organ style
organ = song.add_track(Track(name="organ", instrument="organ", volume=0.45, pan=-0.15))
prog = [
    Chord("E", "min", 3, duration=BAR),
    Chord("G", "maj", 3, duration=BAR),
    Chord("A", "min", 3, duration=BAR),
    Chord("B", "min", 3, duration=BAR),
]
organ.extend(prog * 6)

# Lead - angular melody
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=0.2))
mel = [
    Note("E", 5, 0.5),
    Note("G", 5, 0.5),
    Note("B", 5, 0.5),
    Note("A", 5, 0.5),
    Note("F#", 5, 0.5),
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("B", 4, 0.5),
    Note("D", 5, 1.0),
    Note("E", 5, 0.5),
    r(0.5),
    Note("G", 5, 0.5),
    Note("A", 5, 0.5),
    Note("B", 5, 0.5),
]
lead.extend(mel * 12)

# Drums - 7/8 groove
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.65))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35))
for _ in range(24):
    kick.extend([Note("C", 2, 0.5), r(1.0), Note("C", 2, 0.5), r(1.0), Note("C", 2, 0.5)])
    snare.extend([r(1.0), Note("D", 3, 0.5), r(1.0), Note("D", 3, 0.5), r(0.5)])
    hat.extend([Note("F", 5, 0.5, velocity=40)] * 7)

song.effects = {
    "lead": EffectsChain().add(delay, delay_ms=306.0, feedback=0.3, wet=0.2),
    "organ": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
}
