from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from app.providers.story_visual_planner import analyze_story


class LocalVideoProvider:
    """
    Free local Blender 3D video provider.

    Pipeline:
        Story
          -> Story Visual Planner
          -> Blender 3D
          -> PNG frames
          -> FFmpeg
          -> MP4
          -> FFprobe verification
    """

    def __init__(self):
        self.blender = os.getenv(
            "AADWIK_BLENDER_PATH",
            r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
        )

        self.ffmpeg = os.getenv(
            "AADWIK_FFMPEG_PATH",
            r"C:\ffmpeg-n9.0-latest-win64-gpl-9.0\bin\ffmpeg.exe",
        )

        self.ffprobe = os.getenv(
            "AADWIK_FFPROBE_PATH",
            str(Path(self.ffmpeg).with_name("ffprobe.exe")),
        )

        # Current development render settings.
        self.width = 640
        self.height = 360
        self.fps = 8

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def _check_executable(self, path: str, name: str):
        executable = Path(path)

        if not executable.exists():
            raise FileNotFoundError(
                f"{name} executable not found: {executable}"
            )

        if not executable.is_file():
            raise FileNotFoundError(
                f"{name} path is not a file: {executable}"
            )

    # ------------------------------------------------------------------
    # Main generation
    # ------------------------------------------------------------------

    def generate_video(
        self,
        prompt,
        output_path,
        aspect_ratio="16:9",
        style=None,
        production_plan=None,
        **kwargs,
    ):
        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------------------
        # Validate local tools
        # --------------------------------------------------------------

        self._check_executable(
            self.blender,
            "Blender",
        )

        self._check_executable(
            self.ffmpeg,
            "FFmpeg",
        )

        self._check_executable(
            self.ffprobe,
            "FFprobe",
        )

        # --------------------------------------------------------------
        # Build / receive production plan
        # --------------------------------------------------------------

        if production_plan is not None:
            plan = production_plan
        else:
            plan = analyze_story(
                str(prompt),
                style=style or "stylized cinematic 3D",
                aspect_ratio=aspect_ratio,
            )

        if not isinstance(plan, dict):
            raise RuntimeError(
                "Story visual planner returned an invalid production plan."
            )

        title = plan.get(
            "title",
            "Untitled Aadwik Movie",
        )

        production_summary = plan.get(
            "production_summary",
            {},
        )

        scene_count = production_summary.get(
            "scene_count",
            0,
        )

        shot_count = production_summary.get(
            "shot_count",
            0,
        )

        print()
        print("=" * 60)
        print("[AADWIK 3D] LOCAL VIDEO PROVIDER")
        print("=" * 60)
        print("[AADWIK 3D] STORY:", title)
        print("[AADWIK 3D] SCENES:", scene_count)
        print("[AADWIK 3D] SHOTS:", shot_count)
        print("[AADWIK 3D] BLENDER:", self.blender)
        print("[AADWIK 3D] FFMPEG:", self.ffmpeg)
        print("[AADWIK 3D] FFPROBE:", self.ffprobe)
        print("=" * 60)

        # --------------------------------------------------------------
        # Temporary production workspace
        # --------------------------------------------------------------

        work = Path(
            tempfile.mkdtemp(
                prefix="aadwik_3d_"
            )
        )

        try:
            plan_file = work / "plan.json"

            frames_dir = work / "frames"

            frames_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            # ----------------------------------------------------------
            # Save production plan
            # ----------------------------------------------------------

            plan_file.write_text(
                json.dumps(
                    plan,
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            # ----------------------------------------------------------
            # Blender scene script
            # ----------------------------------------------------------

            scene_script = Path(
                __file__
            ).with_name(
                "aadwik_blender_scene.py"
            )

            if not scene_script.exists():
                raise FileNotFoundError(
                    "Aadwik Blender scene script not found: "
                    f"{scene_script}"
                )

            # ----------------------------------------------------------
            # Blender command
            # ----------------------------------------------------------

            blender_cmd = [
                self.blender,
                "-b",
                "--python",
                str(scene_script),
                "--",
                "--plan",
                str(plan_file),
                "--out",
                str(frames_dir),
                "--width",
                str(self.width),
                "--height",
                str(self.height),
                "--fps",
                str(self.fps),
            ]

            print("[AADWIK 3D] STARTING BLENDER...")

            blender_result = subprocess.run(
                blender_cmd,
                check=False,
            )

            if blender_result.returncode != 0:
                raise RuntimeError(
                    "Blender rendering failed with exit code "
                    f"{blender_result.returncode}"
                )

            print("[AADWIK 3D] BLENDER COMPLETE")

            # ----------------------------------------------------------
            # Collect rendered frames
            # ----------------------------------------------------------

            images = sorted(
                frames_dir.glob(
                    "frame_*.png"
                )
            )

            if not images:
                raise RuntimeError(
                    "Blender completed but produced no PNG frames."
                )

            print(
                "[AADWIK 3D] RENDERED PNG FRAMES:",
                len(images),
            )

            # ----------------------------------------------------------
            # FFmpeg input pattern
            #
            # The Blender pipeline produces:
            # frame_000001.png
            # frame_000002.png
            # ...
            #
            # FFmpeg expects:
            # frame_%06d.png
            # ----------------------------------------------------------

            frame_pattern = str(
                frames_dir / "frame_%06d.png"
            )

            # ----------------------------------------------------------
            # FFmpeg encoding
            # ----------------------------------------------------------

            ffmpeg_cmd = [
                self.ffmpeg,
                "-y",
                "-framerate",
                str(self.fps),
                "-start_number",
                "1",
                "-i",
                frame_pattern,
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(output_path),
            ]

            print("[AADWIK 3D] ENCODING MP4...")

            ffmpeg_result = subprocess.run(
                ffmpeg_cmd,
                check=False,
            )

            if ffmpeg_result.returncode != 0:
                raise RuntimeError(
                    "FFmpeg encoding failed with exit code "
                    f"{ffmpeg_result.returncode}"
                )

            # ----------------------------------------------------------
            # Basic MP4 validation
            # ----------------------------------------------------------

            if not output_path.exists():
                raise RuntimeError(
                    "FFmpeg completed but MP4 file does not exist."
                )

            file_size = output_path.stat().st_size

            if file_size <= 0:
                raise RuntimeError(
                    "FFmpeg produced an empty MP4 file."
                )

            print(
                "[AADWIK 3D] MP4 CREATED:",
                output_path,
            )

            print(
                "[AADWIK 3D] MP4 SIZE:",
                file_size,
                "bytes",
            )

            # ----------------------------------------------------------
            # FFprobe validation
            #
            # IMPORTANT:
            # Do NOT depend on nb_read_frames / nb_read_packets.
            # Those values can return 0 depending on the FFprobe build
            # and MP4 container metadata even when the video is valid.
            #
            # Instead we verify:
            #   1. video stream exists
            #   2. duration exists
            #   3. duration is greater than zero
            # ----------------------------------------------------------

            probe_cmd = [
                self.ffprobe,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=codec_name,width,height,duration",
                "-of",
                "json",
                str(output_path),
            ]

            print("[AADWIK 3D] VERIFYING MP4...")

            probe_result = subprocess.run(
                probe_cmd,
                check=False,
                capture_output=True,
                text=True,
            )

            if probe_result.returncode != 0:
                raise RuntimeError(
                    "FFprobe failed with exit code "
                    f"{probe_result.returncode}: "
                    f"{probe_result.stderr.strip()}"
                )

            probe_text = (
                probe_result.stdout or ""
            ).strip()

            if not probe_text:
                raise RuntimeError(
                    "FFprobe returned no video information."
                )

            try:
                probe_data = json.loads(
                    probe_text
                )
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    "FFprobe returned invalid JSON."
                ) from exc

            streams = probe_data.get(
                "streams",
                [],
            )

            if not streams:
                raise RuntimeError(
                    "FFprobe could not find a video stream."
                )

            video_stream = streams[0]

            codec = video_stream.get(
                "codec_name"
            )

            width = video_stream.get(
                "width"
            )

            height = video_stream.get(
                "height"
            )

            duration_raw = video_stream.get(
                "duration"
            )

            try:
                duration = float(
                    duration_raw
                )
            except (
                TypeError,
                ValueError,
            ):
                duration = 0.0

            if duration <= 0:
                # Some MP4 files expose duration at the format level
                # rather than the stream level.
                format_probe_cmd = [
                    self.ffprobe,
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(output_path),
                ]

                format_probe = subprocess.run(
                    format_probe_cmd,
                    check=False,
                    capture_output=True,
                    text=True,
                )

                try:
                    duration = float(
                        (
                            format_probe.stdout
                            or "0"
                        ).strip()
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    duration = 0.0

            if duration <= 0:
                raise RuntimeError(
                    "MP4 verification failed: "
                    "video duration is zero or unavailable."
                )

            print(
                "[AADWIK 3D] VIDEO STREAM:",
                codec or "unknown",
            )

            print(
                "[AADWIK 3D] RESOLUTION:",
                f"{width}x{height}",
            )

            print(
                "[AADWIK 3D] DURATION:",
                f"{duration:.2f}s",
            )

            # ----------------------------------------------------------
            # Estimate expected duration from rendered frames
            # ----------------------------------------------------------

            expected_duration = (
                len(images) / self.fps
            )

            # Allow a small container/encoding difference.
            minimum_duration = (
                expected_duration * 0.90
            )

            if duration < minimum_duration:
                raise RuntimeError(
                    "MP4 duration verification failed: "
                    f"rendered_frames={len(images)}, "
                    f"fps={self.fps}, "
                    f"expected_duration={expected_duration:.2f}s, "
                    f"actual_duration={duration:.2f}s"
                )

            # ----------------------------------------------------------
            # SUCCESS
            # ----------------------------------------------------------

            print()
            print("=" * 60)
            print("[AADWIK 3D] SUCCESS")
            print("=" * 60)
            print(
                "[AADWIK 3D] FRAMES:",
                len(images),
            )
            print(
                "[AADWIK 3D] DURATION:",
                f"{duration:.2f}s",
            )
            print(
                "[AADWIK 3D] OUTPUT:",
                output_path,
            )
            print("=" * 60)
            print()

            return str(
                output_path
            )

        finally:
            shutil.rmtree(
                work,
                ignore_errors=True,
            )


# ----------------------------------------------------------------------
# Aadwik compatibility aliases
# ----------------------------------------------------------------------

local_video_provider = LocalVideoProvider()

video_provider = local_video_provider

VideoProvider = LocalVideoProvider