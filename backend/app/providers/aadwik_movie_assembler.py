import json
from pathlib import Path
def assemble_movie():
    p={"schema":"aadwik-movie-assembly-1.0","story":"The Last Star",
       "scenes":14,"shots":41,
       "video":"timeline","audio":"synchronized_audio",
       "compositing":True,"titles":True,"subtitles":True,
       "export_ready":True}
    Path("step11g_movie_package.json").write_text(json.dumps(p,indent=2),encoding="utf-8")
    return p
