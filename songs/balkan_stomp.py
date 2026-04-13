"""Balkan Stomp — aksak rhythms in 7/8 and 11/8 with displaced melody."""

from code_music import EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import aksak, displace

song = Song(title="Balkan Stomp", bpm=160, time_sig=(7, 8))

# 7/8 aksak kick pattern (2+2+3)
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.6))
kick.extend(aksak("7/8", "C", 2, bars=8))

# Hat on every subdivision
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.25))
for _ in range(56):  # 7 * 8 bars
    hat.add(Note("C", 5, 0.25))

# Bass following the aksak accents
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for _ in range(8):
    bass.extend([Note("D", 2, 0.5), Note("D", 2, 0.5), Note("D", 2, 0.75)])

# Melody displaced by half a beat for tension
melody_raw = [
    Note("D", 5, 0.5),
    Note("F", 5, 0.25),
    Note("A", 5, 0.25),
    Note("G", 5, 0.5),
    Note("F", 5, 0.25),
    Note("E", 5, 0.25),
]
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=0.15))
for _ in range(8):
    lead.extend(displace(melody_raw, 0.25))

song.effects = {
    "lead": EffectsChain().add(delay, delay_ms=214, feedback=0.2, wet=0.15),
    "bass": EffectsChain().add(reverb, room_size=0.3, wet=0.15),
}
