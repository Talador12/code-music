"""Arp pattern showcase: all 8 ARP_PATTERNS on an Am7 chord."""

from code_music import ARP_PATTERNS, Chord, Note, Song, Track, arp

song = Song(title="arp_patterns", bpm=120)
c = Chord("A", "min7", 4)
for name in ARP_PATTERNS:
    tr = song.add_track(Track(name=name, instrument="pluck", volume=0.7))
    tr.extend(arp(c, pattern=name, rate=0.25, octaves=2))
    tr.add(Note.rest(1.0))
