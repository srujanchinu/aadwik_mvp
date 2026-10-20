from pathlib import Path
import os, shutil, subprocess, tempfile

BLENDER=Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
FFMPEG=Path(r"C:\ffmpeg-n9.0-latest-win64-gpl-9.0\bin\ffmpeg.exe")
SCENE=Path(__file__).with_name("aadwik_animation_scene.py")

class LocalVideoProvider:
    def __init__(self): self.name="Aadwik Real 3D Cartoon Animation"
    def generate_video(self,prompt,output_path,aspect_ratio="16:9",style=None,**kwargs):
        out=Path(output_path);out.parent.mkdir(parents=True,exist_ok=True)
        w,h=(360,640) if aspect_ratio=="9:16" else ((512,512) if aspect_ratio=="1:1" else (640,360))
        fps=int(kwargs.get("fps",8)); work=Path(tempfile.mkdtemp(prefix="aadwik_anim_",dir=str(out.parent))); frames=work/"frames";frames.mkdir()
        try:
            for p,label in ((BLENDER,"Blender"),(FFMPEG,"FFmpeg"),(SCENE,"animation scene")):
                if not p.exists(): raise FileNotFoundError(f"{label} not found: {p}")
            cmd=[str(BLENDER),"-b","-P",str(SCENE),"--","--frames_dir",str(frames),"--width",str(w),"--height",str(h),"--fps",str(fps),"--prompt",str(prompt or "")]
            r=subprocess.run(cmd,cwd=str(work),text=True,check=False)
            if r.returncode!=0: raise RuntimeError(f"Blender animation failed with exit code {r.returncode}.")
            files=sorted(frames.rglob("*.png"),key=lambda p:p.name)
            if not files: raise RuntimeError("3D animation renderer produced no PNG frames.")
            # concat at fixed fps
            concat=work/"concat.txt"
            with concat.open("w",encoding="utf-8") as f:
                for p in files:f.write("file '"+p.resolve().as_posix().replace("'","'\\''")+"'\n")
            video=work/"final.mp4"
            rr=subprocess.run([str(FFMPEG),"-y","-f","concat","-safe","0","-i",str(concat),"-vf",f"scale={w}:{h}:flags=lanczos","-r",str(fps),"-c:v","libx264","-pix_fmt","yuv420p","-movflags","+faststart",str(video)],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            if rr.returncode!=0: raise RuntimeError("FFmpeg failed:\n"+rr.stderr[-3000:])
            shutil.copy2(video,out);return str(out)
        finally:shutil.rmtree(work,ignore_errors=True)

local_video_provider=LocalVideoProvider
video_provider=LocalVideoProvider
VideoProvider=LocalVideoProvider
