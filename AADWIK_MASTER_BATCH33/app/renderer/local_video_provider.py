from pathlib import Path
import os
import shutil
import subprocess
import tempfile

BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
FFMPEG = Path(r"C:\ffmpeg-n9.0-latest-win64-gpl-9.0\bin\ffmpeg.exe")
FFPROBE = FFMPEG.with_name("ffprobe.exe")
SCENE = Path(__file__).with_name("aadwik_animation_scene.py")

class LocalVideoProvider:
    def __init__(self):
        self.name = "Aadwik Real 3D Cartoon Animation"

    def generate_video(self, prompt, output_path, aspect_ratio="16:9", style=None, **kwargs):
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        w, h = (360, 640) if aspect_ratio == "9:16" else (
            (512, 512) if aspect_ratio == "1:1" else (640, 360)
        )
        fps = int(kwargs.get("fps", 8))
        expected_shots = int(kwargs.get("expected_shots", 8))
        shot_seconds = float(kwargs.get("shot_seconds", 2.0))
        expected_frames = int(round(expected_shots * shot_seconds * fps))
        min_frames = int(kwargs.get("min_frames", expected_frames))

        work = Path(tempfile.mkdtemp(prefix="aadwik_anim_", dir=str(out.parent)))
        frames = work / "frames"
        frames.mkdir()

        try:
            for p, label in (
                (BLENDER, "Blender"),
                (FFMPEG, "FFmpeg"),
                (SCENE, "animation scene"),
            ):
                if not p.exists():
                    raise FileNotFoundError(f"{label} not found: {p}")

            cmd = [
                str(BLENDER), "-b", "-P", str(SCENE), "--",
                "--frames_dir", str(frames),
                "--width", str(w), "--height", str(h),
                "--fps", str(fps), "--prompt", str(prompt or ""),
            ]

            r = subprocess.run(
                cmd, cwd=str(work), text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                check=False,
            )
            log = r.stdout or ""
            (work / "blender.log").write_text(log, encoding="utf-8", errors="ignore")

            if r.returncode != 0:
                raise RuntimeError(
                    f"Blender animation failed with exit code {r.returncode}.\n"
                    f"Last Blender output:\n{log[-5000:]}"
                )

            files = sorted(frames.rglob("*.png"), key=lambda p: p.name)
            frame_count = len(files)
            print(f"[AADWIK ANIMATION VERIFY] PNG frames: {frame_count}/{expected_frames}")

            if frame_count < min_frames:
                raise RuntimeError(
                    f"Invalid 3D render: expected at least {min_frames} PNG frames, "
                    f"but Blender produced {frame_count}."
                )

            concat = work / "concat.txt"
            with concat.open("w", encoding="utf-8") as f:
                for p in files:
                    safe = p.resolve().as_posix().replace("'", "'\\''")
                    f.write(f"file '{safe}'\n")

            video = work / "final.mp4"
            rr = subprocess.run(
                [
                    str(FFMPEG), "-y", "-f", "concat", "-safe", "0",
                    "-i", str(concat),
                    "-vf", f"scale={w}:{h}:flags=lanczos",
                    "-r", str(fps), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    str(video),
                ],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                check=False,
            )
            if rr.returncode != 0:
                raise RuntimeError("FFmpeg failed:\n" + rr.stderr[-5000:])

            if not video.exists() or video.stat().st_size < 10_000:
                raise RuntimeError("FFmpeg produced an invalid or suspiciously small MP4.")

            duration = None
            probe_frames = None
            if FFPROBE.exists():
                pr = subprocess.run(
                    [
                        str(FFPROBE), "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height,r_frame_rate,nb_frames,duration",
                        "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1",
                        str(video),
                    ],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    check=False,
                )
                probe = [x.strip() for x in pr.stdout.splitlines() if x.strip()]
                (work / "ffprobe.log").write_text(
                    pr.stdout + "\n" + pr.stderr, encoding="utf-8", errors="ignore"
                )
                # Output order: width, height, r_frame_rate, nb_frames, duration, format_duration.
                if len(probe) >= 5:
                    try:
                        probe_frames = int(float(probe[3])) if probe[3] != "N/A" else None
                    except ValueError:
                        probe_frames = None
                    try:
                        duration = float(probe[4])
                    except ValueError:
                        duration = None

            expected_duration = expected_frames / fps
            if duration is not None:
                print(
                    f"[AADWIK ANIMATION VERIFY] MP4 duration: "
                    f"{duration:.3f}s (expected about {expected_duration:.3f}s)"
                )
                if duration < expected_duration * 0.90:
                    raise RuntimeError(
                        f"Invalid final MP4 duration: {duration:.3f}s; "
                        f"expected about {expected_duration:.3f}s."
                    )

            if probe_frames is not None:
                print(
                    f"[AADWIK ANIMATION VERIFY] MP4 frames: "
                    f"{probe_frames} (rendered PNGs: {frame_count})"
                )
                if probe_frames < int(min_frames * 0.90):
                    raise RuntimeError(
                        f"Invalid final MP4 frame count: {probe_frames}; "
                        f"expected at least about {int(min_frames * 0.90)}."
                    )

            shutil.copy2(video, out)
            print(f"[AADWIK ANIMATION VERIFY] SUCCESS: {out}")
            return str(out)

        finally:
            shutil.rmtree(work, ignore_errors=True)

local_video_provider = LocalVideoProvider
video_provider = LocalVideoProvider
VideoProvider = LocalVideoProvider
