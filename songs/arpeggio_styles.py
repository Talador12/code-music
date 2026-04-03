"""Arpeggio Styles — up, down, and updown arpeggios on chord progression."""

from code_music import EffectsChain, Song, Track, reverb
from code_music.theory import arpeggiate_chord

song = Song(title="Arpeggio Styles", bpm=120, sample_rate=44100)
for direction in ["up", "down", "updown"]:
    tr = song.add_track(Track(name=f"arp_{direction}", instrument="piano", volume=0.45))
    for root, shape in [("C", "maj7"), ("A", "min7"), ("F", "maj7"), ("G", "dom7")]:
        tr.extend(arpeggiate_chord(root, shape, duration=0.25, direction=direction))
song.effects = {"arp_up": EffectsChain().add(reverb, room_size=0.4, wet=0.15)}
