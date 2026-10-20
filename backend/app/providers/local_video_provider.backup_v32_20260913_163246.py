from __future__ import annotations
import os, shutil, subprocess, tempfile
from pathlib import Path
from typing import Optional

BLENDER_EXE=Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
FFMPEG_EXE=Path(r"C:\ffmpeg-n9.0-latest-win64-gpl-9.0\bin\ffmpeg.exe")
SCENE_SCRIPT=Path(__file__).with_name("aadwik_blender_scene.py")

class LocalVideoProvider:
    def __init__(self): self.name="Aadwik Local Story-Aware Cartoon 3D"
    def generate_video(self,prompt:str,output_path:str|Path,aspect_ratio:str="16:9",style:Optional[str]=None,**kwargs):
        output=Path(output_path); output.parent.mkdir(parents=True,exist_ok=True)
        w,h=self._resolution(aspect_ratio); fps=int(kwargs.get("fps",8))
        work=Path(tempfile.mkdtemp(prefix="aadwik_cartoon_",dir=str(output.parent))); frames=work/"frames"; frames.mkdir()
        try:
            self._validate()
            cmd=[str(BLENDER_EXE),"-b","-P",str(SCENE_SCRIPT),"--","--frames_dir",str(frames),
                 "--width",str(w),"--height",str(h),"--fps",str(fps),"--prompt",str(prompt or "")]
            print("\n"+"="*70+"\n[AADWIK CARTOON 3D] STARTING\n"+"="*70)
            r=subprocess.run(cmd,cwd=str(work),text=True,check=False)
            if r.returncode!=0: raise RuntimeError(f"Blender failed with exit code {r.returncode}.")
            files=sorted(frames.rglob("*.png"),key=self._sort_key)
            print(f"[AADWIK CARTOON 3D] PNG frames: {len(files)}")
            if not files: raise RuntimeError("Cartoon renderer produced no PNG frames.")
            concat=work/"concat.txt"
            with concat.open("w",encoding="utf-8") as f:
                for p in files:
                    s=p.resolve().as_posix().replace("'","'\\''")
                    f.write("file '"+s+"'\n")
            v=work/"video.mp4"
            cmd2=[str(FFMPEG_EXE),"-y","-f","concat","-safe","0","-i",str(concat),
                  "-vf",f"scale={w}:{h}:flags=lanczos","-r",str(fps),"-c:v","libx264","-pix_fmt","yuv420p",str(v)]
            e=subprocess.run(cmd2,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
            if e.returncode!=0: raise RuntimeError("FFmpeg encoding failed:\n"+e.stderr[-3000:])
            shutil.copy2(v,output)
            if not output.exists() or output.stat().st_size==0: raise RuntimeError("Final MP4 was not created.")
            print(f"[AADWIK CARTOON 3D] SUCCESS: {output}")
            return str(output)
        finally: shutil.rmtree(work,ignore_errors=True)
    @staticmethod
    def _resolution(a):
        return (360,640) if a=="9:16" else ((512,512) if a=="1:1" else (640,360))
    @staticmethod
    def _sort_key(p):
        nums=[]; cur=""
        for c in p.stem:
            if c.isdigit(): cur+=c
            elif cur: nums.append(int(cur)); cur=""
        if cur: nums.append(int(cur))
        return tuple(nums),p.name
    def _validate(self):
        for p,label in ((BLENDER_EXE,"Blender"),(FFMPEG_EXE,"FFmpeg"),(SCENE_SCRIPT,"scene script")):
            if not p.exists(): raise FileNotFoundError(f"{label} not found: {p}")

local_video_provider=LocalVideoProvider
video_provider=LocalVideoProvider
VideoProvider=LocalVideoProvider
