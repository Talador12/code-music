"""String Quartet v2 - full quartet using new bowed string presets."""

from code_music import EffectsChain, Note, Song, Track, reverb, scale
from code_music.sound_design import pm_cello, pm_viola, pm_violin

song = Song(title="String Quartet No. 2", bpm=76, sample_rate=44100)
song.register_instrument("pm_violin", pm_violin)
song.register_instrument("pm_viola", pm_viola)
song.register_instrument("pm_cello", pm_cello)

v1 = song.add_track(Track(name="violin_1", instrument="pm_violin", volume=0.5, pan=0.25))
v1.extend(scale("G", "major", octave=5, length=16))

v2 = song.add_track(Track(name="violin_2", instrument="pm_violin", volume=0.45, pan=0.1))
for root in ["G", "B", "D", "G", "A", "B", "A", "G"]:
    v2.add(Note(root, 4, 2.0, velocity=55))

va = song.add_track(Track(name="viola", instrument="pm_viola", volume=0.45, pan=-0.1))
for root in ["D", "D", "A", "B", "C", "D", "C", "B"]:
    va.add(Note(root, 4, 2.0, velocity=50))

vc = song.add_track(Track(name="cello", instrument="pm_cello", volume=0.5, pan=-0.25))
for root in ["G", "G", "D", "G", "C", "G", "D", "G"]:
    vc.add(Note(root, 2, 2.0, velocity=55))

song.effects = {
    name: EffectsChain().add(reverb, room_size=0.6, wet=0.25)
    for name in ["violin_1", "violin_2", "viola", "cello"]
}
