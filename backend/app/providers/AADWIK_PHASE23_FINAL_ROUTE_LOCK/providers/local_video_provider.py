
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

try:
    from app.engines.story_engine import analyze_story
except Exception:
    def analyze_story(prompt: str, **kwargs):
        return {
            "title": "Aadwik Production",
            "story": prompt,
            "scenes": [
                {
                    "title": "Opening",
                    "description": prompt,
                    "location": {"kind": "forest"},
                    "characters": ["Tara", "Guardian"],
                    "props": ["star"],
                    "emotion": "wonder",
                }
            ],
        }


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROVIDER_DIR = Path(__file__).resolve().parent
SCENE_SCRIPT = PROVIDER_DIR / "aadwik_blender_scene.py"

BLENDER_EXE = Path(
    os.environ.get(
        "AADWIK_BLENDER_EXE",
        r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    )
)

FFMPEG_EXE = Path(
    os.environ.get(
        "AADWIK_FFMPEG_EXE",
        r"C:\ffmpeg-n9.0-latest-win64-gpl-9.0\bin\ffmpeg.exe",
    )
)

FFPROBE_EXE = Path(
    os.environ.get(
        "AADWIK_FFPROBE_EXE",
        r"C:\ffmpeg-n9.0-latest-win64-gpl-9.0\bin\ffprobe.exe",
    )
)


class LocalVideoProvider:
    """
    Canonical Aadwik local 3D development provider.

    Critical rule:
    The final MP4 is ALWAYS encoded from this generation's own
    Phase 23 rendered_frames directory.

    It never reads backend\\frames, backend\\ffmpeg_sequence,
    blender_test_frames, step8h_sequence, or any other legacy folder.
    """

    def __init__(
        self,
        blender_path: Path | str = BLENDER_EXE,
        ffmpeg_path: Path | str = FFMPEG_EXE,
        ffprobe_path: Path | str = FFPROBE_EXE,
    ):
        self.blender_path = Path(blender_path)
        self.ffmpeg_path = Path(ffmpeg_path)
        self.ffprobe_path = Path(ffprobe_path)

    def _check_tools(self):
        for label, path in (
            ("Blender", self.blender_path),
            ("FFmpeg", self.ffmpeg_path),
            ("FFprobe", self.ffprobe_path),
        ):
            if not path.exists():
                raise FileNotFoundError(
                    f"{label} not found: {path}"
                )

        if not SCENE_SCRIPT.exists():
            raise FileNotFoundError(
                f"Phase 23 scene not found: {SCENE_SCRIPT}"
            )

    def _make_plan(
        self,
        prompt: str,
        plan_path: Path,
        **kwargs: Any,
    ):
        try:
            plan = analyze_story(
                prompt,
                **kwargs,
            )
        except TypeError:
            plan = analyze_story(prompt)

        if not isinstance(plan, dict):
            plan = {
                "title": "Aadwik Production",
                "story": prompt,
                "scenes": [],
            }

        plan.setdefault("title", "Aadwik Production")
        plan.setdefault("story", prompt)

        if not isinstance(plan.get("scenes"), list) or not plan["scenes"]:
            plan["scenes"] = [
                {
                    "title": "Opening",
                    "description": prompt,
                    "location": {"kind": "forest"},
                    "characters": ["Tara", "Guardian"],
                    "props": ["star"],
                    "emotion": "wonder",
                }
            ]

        plan["aadwik_visual_pipeline"] = "PHASE_23_FINAL_ROUTE_LOCK"
        plan["character_library"] = str(
            PROVIDER_DIR / "aadwik_character_quality.py"
        )
        plan["scene_script"] = str(SCENE_SCRIPT)

        plan_path.write_text(
            json.dumps(plan, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return plan

    def _run_blender(
        self,
        plan_path: Path,
        frames_dir: Path,
        width: int,
        height: int,
        fps: int,
    ):
        frames_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            str(self.blender_path),
            "-b",
            "-P",
            str(SCENE_SCRIPT),
            "--",
            "--plan",
            str(plan_path),
            "--out",
            str(frames_dir),
            "--width",
            str(width),
            "--height",
            str(height),
            "--fps",
            str(fps),
        ]

        env = os.environ.copy()
        env["PYTHONPATH"] = (
            str(PROVIDER_DIR)
            + os.pathsep
            + env.get("PYTHONPATH", "")
        )

        print(
            "[AADWIK FINAL ROUTE] Blender command:",
            " ".join(f'"{x}"' if " " in x else x for x in cmd),
            flush=True,
        )

        result = subprocess.run(
            cmd,
            cwd=str(BACKEND_DIR),
            env=env,
            text=True,
            capture_output=True,
        )

        if result.stdout:
            print(result.stdout, flush=True)

        if result.stderr:
            print(result.stderr, flush=True)

        if result.returncode != 0:
            raise RuntimeError(
                f"Blender failed with exit code {result.returncode}."
            )

        frames = sorted(frames_dir.glob("frame_*.png"))

        if not frames:
            raise RuntimeError(
                "Phase 23 produced no PNG frames."
            )

        print(
            f"[AADWIK FINAL ROUTE] Phase 23 frames: {len(frames)}",
            flush=True,
        )

        return frames

    def _encode(
        self,
        frames_dir: Path,
        output_path: Path,
        fps: int,
    ):
        frames = sorted(frames_dir.glob("frame_*.png"))

        if not frames:
            raise RuntimeError(
                "Cannot encode: no Phase 23 frames exist."
            )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Never reuse an existing MP4.
        if output_path.exists():
            output_path.unlink()

        cmd = [
            str(self.ffmpeg_path),
            "-y",
            "-framerate",
            str(fps),
            "-start_number",
            "1",
            "-i",
            str(frames_dir / "frame_%06d.png"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output_path),
        ]

        print(
            "[AADWIK FINAL ROUTE] Encoding ONLY:",
            frames_dir,
            flush=True,
        )

        result = subprocess.run(
            cmd,
            cwd=str(BACKEND_DIR),
            text=True,
            capture_output=True,
        )

        if result.returncode != 0:
            print(result.stdout, flush=True)
            print(result.stderr, flush=True)
            raise RuntimeError(
                f"FFmpeg failed with exit code {result.returncode}."
            )

        if not output_path.exists() or output_path.stat().st_size < 1024:
            raise RuntimeError(
                "FFmpeg completed but final MP4 is missing or invalid."
            )

    def _validate_mp4(
        self,
        output_path: Path,
        width: int,
        height: int,
        fps: int,
        expected_frames: int,
    ):
        cmd = [
            str(self.ffprobe_path),
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name,width,height,avg_frame_rate,duration",
            "-of",
            "json",
            str(output_path),
        ]

        result = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "FFprobe could not validate the final MP4."
            )

        data = json.loads(result.stdout)
        streams = data.get("streams", [])

        if not streams:
            raise RuntimeError(
                "Final MP4 contains no video stream."
            )

        stream = streams[0]

        if stream.get("codec_name") != "h264":
            raise RuntimeError(
                f"Unexpected video codec: {stream.get('codec_name')}"
            )

        if int(stream.get("width", 0)) != width:
            raise RuntimeError("Final MP4 width mismatch.")

        if int(stream.get("height", 0)) != height:
            raise RuntimeError("Final MP4 height mismatch.")

        print(
            "[AADWIK FINAL ROUTE] MP4 VALIDATED:",
            output_path,
            flush=True,
        )

    def generate_video(
        self,
        prompt: str,
        output_path: str | Path,
        aspect_ratio: str = "16:9",
        style: str | None = None,
        **kwargs: Any,
    ):
        self._check_tools()

        output_path = Path(output_path).resolve()

        # Permanent per-movie work directory.
        # This intentionally lives beside the final MP4 so the generated
        # Phase 23 frames remain inspectable and can never be confused with
        # legacy global folders.
        work_dir = output_path.parent / (
            output_path.stem + "_phase23"
        )

        if work_dir.exists():
            shutil.rmtree(work_dir, ignore_errors=True)

        work_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        plan_path = work_dir / "phase23_production_plan.json"
        frames_dir = work_dir / "rendered_frames"

        if aspect_ratio == "9:16":
            width, height = 360, 640
        elif aspect_ratio == "1:1":
            width, height = 480, 480
        else:
            width, height = 640, 360

        fps = int(kwargs.get("fps", 8))

        print("=" * 70, flush=True)
        print(
            "AADWIK PHASE 23 FINAL ROUTE LOCK",
            flush=True,
        )
        print(
            "[AADWIK FINAL ROUTE] Scene:",
            SCENE_SCRIPT,
            flush=True,
        )
        print(
            "[AADWIK FINAL ROUTE] Character library:",
            PROVIDER_DIR / "aadwik_character_quality.py",
            flush=True,
        )
        print(
            "[AADWIK FINAL ROUTE] Work directory:",
            work_dir,
            flush=True,
        )
        print(
            "[AADWIK FINAL ROUTE] Final MP4:",
            output_path,
            flush=True,
        )
        print("=" * 70, flush=True)

        self._make_plan(
            prompt,
            plan_path,
            style=style,
            aspect_ratio=aspect_ratio,
            **kwargs,
        )

        frames = self._run_blender(
            plan_path,
            frames_dir,
            width,
            height,
            fps,
        )

        self._encode(
            frames_dir,
            output_path,
            fps,
        )

        self._validate_mp4(
            output_path,
            width,
            height,
            fps,
            len(frames),
        )

        print(
            "[AADWIK FINAL ROUTE] SUCCESS:",
            output_path,
            flush=True,
        )

        return output_path


local_video_provider = LocalVideoProvider()
video_provider = local_video_provider
VideoProvider = LocalVideoProvider
