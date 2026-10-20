from pathlib import Path
from datetime import datetime
import shutil

BATCH=Path(__file__).resolve().parents[1]
ROOT=None
for p in BATCH.parents:
    if (p/"backend").is_dir() and (p/"mobile").is_dir(): ROOT=p;break
if ROOT is None: raise SystemExit("ERROR: Aadwik project root not found.")
SRC=BATCH/"app"/"renderer";TARGET=ROOT/"backend"/"app"/"providers"
def install(src,dst):
    TARGET.mkdir(parents=True,exist_ok=True)
    if dst.exists():
        stamp=datetime.now().strftime("%Y%m%d_%H%M%S");b=dst.with_name(dst.stem+f".backup_v32_{stamp}"+dst.suffix);shutil.copy2(dst,b);print("Backup:",b)
    shutil.copy2(src,dst);print("Installed:",dst)
print("AADWIK Batch 32 — real 3D cartoon animation renderer")
print("Project root:",ROOT)
install(SRC/"aadwik_animation_scene.py",TARGET/"aadwik_blender_scene.py")
install(SRC/"local_video_provider_animation.py",TARGET/"local_video_provider.py")
print("Batch 32 animation renderer installed.")
