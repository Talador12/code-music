"""Data Driven — song defined as JSON data, loaded and rendered."""

import json

from code_music import EffectsChain, reverb
from code_music.serialization import song_from_json

# Define a song entirely as JSON data
SONG_JSON = json.dumps(
    {
        "version": "1.0",
        "title": "Data Driven",
        "bpm": 115,
        "sample_rate": 44100,
        "time_sig": [4, 4],
        "composer": "JSON",
        "key_sig": "Em",
        "tracks": [
            {
                "name": "lead",
                "instrument": "piano",
                "volume": 0.5,
                "pan": 0.15,
                "swing": 0.0,
                "density": 1.0,
                "density_seed": None,
                "beats": [
                    {"event": {"pitch": "E", "octave": 5, "duration": 1.0, "velocity": 0.8}},
                    {"event": {"pitch": "G", "octave": 5, "duration": 0.5, "velocity": 0.8}},
                    {"event": {"pitch": "B", "octave": 5, "duration": 1.5, "velocity": 0.8}},
                    {"event": {"pitch": "A", "octave": 5, "duration": 1.0, "velocity": 0.8}},
                    {"event": {"pitch": "G", "octave": 5, "duration": 0.5, "velocity": 0.8}},
                    {"event": {"pitch": "E", "octave": 5, "duration": 1.0, "velocity": 0.8}},
                    {"event": {"pitch": "D", "octave": 5, "duration": 0.5, "velocity": 0.8}},
                    {"event": {"pitch": "E", "octave": 5, "duration": 2.0, "velocity": 0.8}},
                ],
            },
            {
                "name": "pad",
                "instrument": "pad",
                "volume": 0.4,
                "pan": -0.1,
                "swing": 0.0,
                "density": 1.0,
                "density_seed": None,
                "beats": [
                    {
                        "event": {
                            "type": "chord",
                            "root": "E",
                            "shape": "min7",
                            "octave": 3,
                            "duration": 4.0,
                            "velocity": 0.65,
                            "inversion": 0,
                        }
                    },
                    {
                        "event": {
                            "type": "chord",
                            "root": "C",
                            "shape": "maj7",
                            "octave": 3,
                            "duration": 4.0,
                            "velocity": 0.65,
                            "inversion": 0,
                        }
                    },
                ],
            },
            {
                "name": "bass",
                "instrument": "bass",
                "volume": 0.5,
                "pan": 0.0,
                "swing": 0.0,
                "density": 1.0,
                "density_seed": None,
                "beats": [
                    {"event": {"pitch": "E", "octave": 2, "duration": 4.0, "velocity": 0.8}},
                    {"event": {"pitch": "C", "octave": 2, "duration": 4.0, "velocity": 0.8}},
                ],
            },
        ],
        "custom_instruments": {},
        "bpm_map": [],
    }
)

song = song_from_json(SONG_JSON)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
print(f"Loaded from JSON: {song.title}, {len(song.tracks)} tracks")
