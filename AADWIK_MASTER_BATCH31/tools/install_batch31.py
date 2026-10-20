from pathlib import Path
from datetime import datetime
import shutil, sys

SCRIPT_DIR = Path(__file__).resolve().parent
BATCH_DIR = SCRIPT_DIR.parent
ROOT = None
for candidate in [BATCH_DIR.parent, *BATCH_DIR.parents]:
    if (candidate / "backend").is_dir() and (candidate / "mobile").is_dir():
        ROOT = candidate
        break
if ROOT is None:
    raise SystemExit("ERROR: Could not locate Aadwik project root containing both backend and mobile folders.")
SRC=BATCH_DIR/"app"/"renderer"
TARGET=ROOT/"backend"/"app"/"providers"
def backup_replace(src,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
        backup=target.with_name(target.stem+f".backup_v31_{stamp}"+target.suffix)
        shutil.copy2(target,backup); print("Backup:",backup)
    shutil.copy2(src,target); print("Installed:",target)

print("AADWIK Batch 31 — story-aware cartoon renderer")
print("Project root:",ROOT)
if not (ROOT/"backend").exists(): raise SystemExit("ERROR: backend folder not found.")
backup_replace(SRC/"aadwik_cartoon_scene.py",TARGET/"aadwik_blender_scene.py")
backup_replace(SRC/"local_video_provider_cartoon.py",TARGET/"local_video_provider.py")
print("Batch 31 cartoon renderer installed.")
print("Blender and FFmpeg executables were not modified.")
