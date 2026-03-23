"""String quartet: four-part harmony, Dm, slow legato."""

from code_music import Note, Song, Track

song = Song(title="string_quartet", bpm=76)
violin1 = song.add_track(Track(name="vln1", instrument="violin", volume=0.7, pan=-0.4))
violin2 = song.add_track(Track(name="vln2", instrument="violin", volume=0.65, pan=-0.2))
viola = song.add_track(Track(name="vla", instrument="strings", volume=0.65, pan=0.2))
cello = song.add_track(Track(name="vc", instrument="cello", volume=0.72, pan=0.4))

vln1_line = [
    Note("F", 5, 2.0),
    Note("E", 5, 1.0),
    Note("D", 5, 1.0),
    Note("C", 5, 2.0),
    Note("A", 4, 2.0),
    Note("A#", 4, 2.0),
    Note("G", 4, 1.0),
    Note("A", 4, 1.0),
    Note("D", 5, 4.0),
]
vln2_line = [
    Note("D", 5, 2.0),
    Note("C", 5, 1.0),
    Note("A", 4, 1.0),
    Note("A", 4, 2.0),
    Note("F", 4, 2.0),
    Note("G", 4, 2.0),
    Note("E", 4, 1.0),
    Note("F", 4, 1.0),
    Note("A", 4, 4.0),
]
viola_line = [
    Note("A", 4, 2.0),
    Note("G", 4, 1.0),
    Note("F", 4, 1.0),
    Note("E", 4, 2.0),
    Note("D", 4, 2.0),
    Note("D", 4, 2.0),
    Note("C", 4, 1.0),
    Note("D", 4, 1.0),
    Note("F", 4, 4.0),
]
cello_line = [
    Note("D", 3, 2.0),
    Note("A", 3, 2.0),
    Note("A", 3, 2.0),
    Note("D", 3, 2.0),
    Note("G", 3, 2.0),
    Note("C", 3, 2.0),
    Note("D", 3, 4.0),
]
violin1.extend(vln1_line)
violin2.extend(vln2_line)
viola.extend(viola_line)
cello.extend(cello_line)
