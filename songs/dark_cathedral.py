"""Dark Cathedral - menacing drones with dark_drone and whisper presets."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.effects import room_reverb
from code_music.sound_design import dark_drone, whisper_pad

song = Song(title="Dark Cathedral", bpm=40, sample_rate=44100)
song.register_instrument("dark_drone", dark_drone)
song.register_instrument("whisper_pad", whisper_pad)

drone = song.add_track(Track(name="drone", instrument="dark_drone", volume=0.4))
drone.add(Note("D", 1, 48.0, velocity=45))

whisper = song.add_track(Track(name="whisper", instrument="whisper_pad", volume=0.25, pan=0.2))
for note in ["D", "F", "A", "D"]:
    whisper.add(Note(note, 4, 12.0, velocity=25))

sub = song.add_track(Track(name="sub", instrument="bass", volume=0.3))
sub.add(Note("D", 1, 48.0, velocity=35))

song.effects = {
    "drone": EffectsChain()
    .add(room_reverb, width=30, depth=40, height=15, absorption=0.08, wet=0.5)
    .add(reverb, room_size=0.98, wet=0.4),
    "whisper": EffectsChain().add(reverb, room_size=0.95, wet=0.5),
}
