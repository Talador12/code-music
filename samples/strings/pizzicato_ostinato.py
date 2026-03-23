"""Pizzicato strings: plucked groove pattern, film-score texture."""

from code_music import Note, Song, Track

song = Song(title="pizzicato_groove", bpm=112)
vln = song.add_track(Track(name="vln", instrument="pizzicato", volume=0.7, pan=-0.3))
vc = song.add_track(Track(name="vc", instrument="pizzicato", volume=0.75, pan=0.3))

vln_pat = [
    Note("E", 5, 0.5),
    Note.rest(0.25),
    Note("G", 5, 0.25),
    Note("F#", 5, 0.5),
    Note.rest(0.25),
    Note("A", 5, 0.25),
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("B", 4, 1.0),
    Note("C", 5, 0.5),
    Note.rest(0.5),
    Note("G", 5, 0.5),
    Note.rest(0.5),
]
vc_pat = [
    Note("E", 3, 0.5),
    Note.rest(0.5),
    Note("B", 3, 0.5),
    Note.rest(0.5),
    Note("A", 3, 0.5),
    Note.rest(0.5),
    Note("F#", 3, 0.5),
    Note.rest(0.5),
]
for _ in range(3):
    vln.extend(vln_pat)
    vc.extend(vc_pat * 2)
