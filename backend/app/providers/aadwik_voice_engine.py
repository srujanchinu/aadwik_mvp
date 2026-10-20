import json
from pathlib import Path

VOICE_SCHEMA="aadwik-voice-profile-1.0"

class VoiceProfile:
    def __init__(self, voice_id, character_id, name, language="en-IN",
                 gender="female", age="young", style="natural",
                 pitch="medium", speed=1.0):
        self.voice_id=voice_id
        self.character_id=character_id
        self.name=name
        self.language=language
        self.gender=gender
        self.age=age
        self.style=style
        self.pitch=pitch
        self.speed=speed

    def to_dict(self):
        return {
            "schema":VOICE_SCHEMA,
            "voice_id":self.voice_id,
            "character_id":self.character_id,
            "name":self.name,
            "language":self.language,
            "gender":self.gender,
            "age":self.age,
            "style":self.style,
            "pitch":self.pitch,
            "speed":self.speed,
        }

class VoiceLibrary:
    def __init__(self):
        self._voices={}

    def register(self, profile):
        if profile.character_id in self._voices:
            raise ValueError("character voice already locked")
        self._voices[profile.character_id]=profile

    def get(self, character_id):
        return self._voices[character_id]

    def manifest(self):
        return {
            "schema":VOICE_SCHEMA,
            "voice_count":len(self._voices),
            "voices":[v.to_dict() for v in self._voices.values()]
        }

def save_manifest(library,path):
    Path(path).write_text(
        json.dumps(library.manifest(),indent=2),encoding="utf-8"
    )
