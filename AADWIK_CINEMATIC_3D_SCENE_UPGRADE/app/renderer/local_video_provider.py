from pathlib import Path
import shutil
import subprocess
import tempfile

BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
FFMPEG = Path(r"C:\ffmpeg-n9.0-latest-win64-gpl-9.0\bin\ffmpeg.exe")
FFPROBE = Path(r"C:\ffmpeg-n9.0-latest-win64-gpl-9.0\bin\ffprobe.exe")
SCENE = Path(__file__).with_name("aadwik_animation_scene.py")

class LocalVideoProvider:
    def __init__(self):
        self.name = "Aadwik Cinematic Real 3D"

    def generate_video(self, prompt, output_path, aspect_ratio="16:9", style=None, **kwargs):
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        if aspect_ratio == "9:16":
            w, h = 360, 640
        elif aspect_ratio == "1:1":
            w, h = 512, 512
        else:
            w, h = 640, 360
        fps = int(kwargs.get("fps", 8))
        expected = int(kwargs.get("frames", 128))
        work = Path(tempfile.mkdtemp(prefix="aadwik_3d_", dir=str(out.parent)))
        frames = work / "frames"
        seq = work / "sequence"
        frames.mkdir()
        seq.mkdir()
        try:
            for p, label in ((BLENDER, "Blender"), (FFMPEG, "FFmpeg"), (SCENE, "3D scene")):
                if not p.exists():
                    raise FileNotFoundError(f"{label} not found: {p}")

            cmd = [
                str(BLENDER), "-b", "-P", str(SCENE), "--",
                "--frames_dir", str(frames),
                "--width", str(w), "--height", str(h),
                "--fps", str(fps), "--frames", str(expected),
                "--prompt", str(prompt or "")
            ]
            r = subprocess.run(cmd, cwd=str(work), text=True, capture_output=True, check=False)
            if r.returncode != 0:
                raise RuntimeError("Blender render failed.\nSTDOUT:\n{}\nSTDERR:\n{}".format(r.stdout, r.stderr))

            files = sorted(frames.rglob("*.png"), key=lambda p: p.name)
            if len(files) != expected:
                raise RuntimeError(f"Invalid 3D render: expected {expected} PNG frames, but Blender produced {len(files)}.")

            for i, p in enumerate(files, 1):
                shutil.copy2(p, seq / f"frame_{i:04d}.png")

            video = work / "final.mp4"
            rr = subprocess.run([
                str(FFMPEG), "-y", "-framerate", str(fps),
                "-i", str(seq / "frame_%04d.png"),
                "-vf", f"scale={w}:{h}:flags=lanczos",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", str(video)
            ], cwd=str(work), text=True, capture_output=True, check=False)
            if rr.returncode != 0:
                raise RuntimeError("FFmpeg assembly failed.\nSTDOUT:\n{}\nSTDERR:\n{}".format(rr.stdout, rr.stderr))

            if not video.exists() or video.stat().st_size < 50000:
                raise RuntimeError("3D MP4 validation failed: output is missing or unexpectedly small.")

            if FFPROBE.exists():
                probe = subprocess.run([
                    str(FFPROBE), "-v", "error", "-show_entries",
                    "format=duration,size", "-of", "default=noprint_wrappers=1",
                    str(video)
                ], text=True, capture_output=True, check=False)
                if probe.returncode != 0:
                    raise RuntimeError("FFprobe validation failed: " + probe.stderr)

            shutil.copy2(video, out)
            return str(out)
        finally:
            shutil.rmtree(work, ignore_errors=True)

local_video_provider = LocalVideoProvider
video_provider = LocalVideoProvider
VideoProvider = LocalVideoProvider
