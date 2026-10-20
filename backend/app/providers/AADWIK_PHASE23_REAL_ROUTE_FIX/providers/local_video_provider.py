from __future__ import annotations

import json
import math
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Optional


BLENDER_EXE = Path(
    r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
)

FFMPEG_EXE = Path(
    r"C:\ffmpeg-n9.0-latest-win64-gpl-9.0\bin\ffmpeg.exe"
)

SCENE_SCRIPT = Path(__file__).with_name("aadwik_blender_scene.py")


class LocalVideoProvider:
    """
    Aadwik local 3D renderer.

    Critical fix:
    Blender renders 128 individual PNGs, but the previous FFmpeg concat
    approach could collapse the image sequence into an extremely short MP4.
    We now normalize the rendered PNGs into ONE sequential frame directory and
    use FFmpeg's image2 demuxer with -framerate. This guarantees:

        128 PNGs @ 8 FPS = 16 seconds

    rather than accidentally producing a 1-2 frame video.
    """

    def __init__(self):
        self.name = "Aadwik Local Blender 3D"

    def generate_video(
        self,
        prompt: str,
        output_path: str | Path,
        aspect_ratio: str = "16:9",
        style: Optional[str] = None,
        **kwargs,
    ):
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        width, height = self._resolution(aspect_ratio)
        fps = int(kwargs.get("fps", 8))

        workdir = Path(
            tempfile.mkdtemp(
                prefix="aadwik_3d_",
                dir=str(output.parent),
            )
        )

        frames_dir = workdir / "rendered_frames"
        sequence_dir = workdir / "sequence"
        frames_dir.mkdir(parents=True, exist_ok=True)
        sequence_dir.mkdir(parents=True, exist_ok=True)

        try:
            self._validate()

            print("")
            print("=" * 70)
            print("AADWIK REAL 3D CINEMATIC PIPELINE")
            print("=" * 70)
            print(f"[AADWIK] Resolution: {width}x{height}")
            print(f"[AADWIK] FPS: {fps}")
            print(f"[AADWIK] Story: {prompt}")
            print("=" * 70)

            # ---------------------------------------------------------------
            # Blender
            # ---------------------------------------------------------------

            plan_path = workdir / "phase23_production_plan.json"
            plan = self._build_phase23_plan(prompt)
            plan_path.write_text(
                json.dumps(plan, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            print(f"[AADWIK] Phase 23 scene: {SCENE_SCRIPT}")
            print(f"[AADWIK] Phase 23 character library: {SCENE_SCRIPT.with_name('aadwik_character_quality.py')}")
            print(f"[AADWIK] Production plan: {plan_path}")

            cmd = [
                str(BLENDER_EXE),
                "-b",
                "-P",
                str(SCENE_SCRIPT),
                "--",
                "--plan",
                str(plan_path),
                "--frames_dir",
                str(frames_dir),
                "--width",
                str(width),
                "--height",
                str(height),
                "--fps",
                str(fps),
            ]

            print("[AADWIK] Starting Blender 5.2...")

            result = subprocess.run(
                cmd,
                cwd=str(workdir),
                check=False,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"Blender failed with exit code {result.returncode}."
                )

            rendered = self._find_png_frames(frames_dir)

            print(
                f"[AADWIK] Blender produced {len(rendered)} PNG frames."
            )

            if not rendered:
                raise RuntimeError(
                    "Blender completed but produced no PNG frames."
                )

            # ---------------------------------------------------------------
            # CRITICAL:
            # Normalize ALL shot files into:
            #
            # sequence/frame_000001.png
            # sequence/frame_000002.png
            # ...
            #
            # This eliminates shot-prefix and FFmpeg concat ambiguity.
            # ---------------------------------------------------------------

            print("[AADWIK] Preparing sequential frame stream...")

            for number, source in enumerate(rendered, start=1):
                destination = sequence_dir / f"frame_{number:06d}.png"

                # copy2 is intentionally used instead of renaming so the
                # original Blender render set remains available for debugging.
                shutil.copy2(source, destination)

            sequence_frames = sorted(sequence_dir.glob("frame_*.png"))

            if len(sequence_frames) != len(rendered):
                raise RuntimeError(
                    "Frame normalization failed: expected "
                    f"{len(rendered)}, got {len(sequence_frames)}."
                )

            expected_duration = len(sequence_frames) / fps

            print(
                f"[AADWIK] Sequential frames: {len(sequence_frames)}"
            )
            print(
                f"[AADWIK] Expected video duration: "
                f"{expected_duration:.2f}s"
            )

            # ---------------------------------------------------------------
            # FFmpeg image sequence
            # ---------------------------------------------------------------

            video_only = workdir / "aadwik_video.mp4"

            print("[AADWIK] Encoding 3D frames with FFmpeg...")

            encode_cmd = [
                str(FFMPEG_EXE),
                "-y",
                "-framerate",
                str(fps),
                "-start_number",
                "1",
                "-i",
                str(sequence_dir / "frame_%06d.png"),
                "-vf",
                (
                    f"scale={width}:{height}:"
                    "force_original_aspect_ratio=decrease,"
                    f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
                ),
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "23",
                "-pix_fmt",
                "yuv420p",
                "-r",
                str(fps),
                "-movflags",
                "+faststart",
                str(video_only),
            ]

            encode = subprocess.run(
                encode_cmd,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            if encode.returncode != 0:
                print(encode.stderr)
                raise RuntimeError(
                    f"FFmpeg encoding failed with exit code "
                    f"{encode.returncode}."
                )

            if not video_only.exists() or video_only.stat().st_size == 0:
                raise RuntimeError("FFmpeg did not create the video.")

            # ---------------------------------------------------------------
            # Verify encoded video BEFORE adding audio.
            #
            # This catches exactly the bug we just encountered.
            # ---------------------------------------------------------------

            encoded_frames, encoded_fps, encoded_duration = (
                self._probe_video(video_only)
            )

            print(
                f"[AADWIK] Encoded video check: "
                f"{encoded_frames} frames, "
                f"{encoded_fps:.2f} FPS, "
                f"{encoded_duration:.2f}s"
            )

            # Allow tiny FFmpeg metadata rounding, but absolutely reject a
            # collapsed 1-2 frame result.
            minimum_expected = max(2, int(len(sequence_frames) * 0.95))

            if encoded_frames < minimum_expected:
                raise RuntimeError(
                    "FFmpeg verification failed. "
                    f"Expected about {len(sequence_frames)} frames, "
                    f"but encoded video contains {encoded_frames}."
                )

            # ---------------------------------------------------------------
            # Audio
            # ---------------------------------------------------------------

            audio = workdir / "aadwik_audio.wav"

            print(
                f"[AADWIK] Creating local cinematic ambience "
                f"({expected_duration:.2f}s)..."
            )

            self._create_audio(
                audio,
                expected_duration,
            )

            # ---------------------------------------------------------------
            # Mux
            # ---------------------------------------------------------------

            print("[AADWIK] Combining video and audio...")

            mux_cmd = [
                str(FFMPEG_EXE),
                "-y",
                "-i",
                str(video_only),
                "-i",
                str(audio),
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-shortest",
                "-movflags",
                "+faststart",
                str(output),
            ]

            mux = subprocess.run(
                mux_cmd,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            if mux.returncode != 0:
                print(mux.stderr)
                raise RuntimeError(
                    f"FFmpeg mux failed with exit code {mux.returncode}."
                )

            if not output.exists() or output.stat().st_size == 0:
                raise RuntimeError("Final MP4 was not created.")

            # ---------------------------------------------------------------
            # Final verification
            # ---------------------------------------------------------------

            final_frames, final_fps, final_duration = (
                self._probe_video(output)
            )

            print("")
            print("=" * 70)
            print("AADWIK REAL 3D VIDEO SUCCESS")
            print("=" * 70)
            print(f"[AADWIK] Final frames: {final_frames}")
            print(f"[AADWIK] Final FPS: {final_fps:.2f}")
            print(f"[AADWIK] Final duration: {final_duration:.2f}s")
            print(
                f"[AADWIK] Size: "
                f"{output.stat().st_size / 1024 / 1024:.2f} MB"
            )
            print(f"[AADWIK] Output: {output}")
            print("=" * 70)

            if final_frames < minimum_expected:
                raise RuntimeError(
                    "Final MP4 verification failed: video was shortened "
                    f"to {final_frames} frames."
                )

            return str(output)

        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    @staticmethod
    def _build_phase23_plan(prompt: str):
        """Create the minimal controlled production plan consumed by Phase 23.

        The important integration rule is that the movie route no longer lets
        Blender choose an unrelated legacy scene. Every render is explicitly
        driven by the Phase 23 scene script and its locked character library.
        """
        story = str(prompt or "").strip()
        if not story:
            story = "A curious girl discovers a glowing blue star in a moonlit forest and helps a tiny guardian return home."

        beats = [
            ("The Beginning", "Curiosity", "wide", "forest", "Introduce Tara and the moonlit forest. "),
            ("The Discovery", "Surprise", "close", "forest", "Tara discovers the glowing blue star. "),
            ("The Guardian", "Wonder", "medium", "forest", "The tiny guardian appears and needs help. "),
            ("The Challenge", "Tension", "medium", "forest", "A shadow creature threatens the journey. "),
            ("The Choice", "Courage", "close", "forest", "Tara chooses compassion and protects the guardian. "),
            ("The Journey", "Determination", "wide", "forest", "Tara and the guardian move toward the safe path home. "),
            ("The Return", "Hope", "close", "forest", "The star opens a path for the guardian to return. "),
            ("The Resolution", "Joy", "wide", "forest", "The guardian returns home and Tara watches the sky brighten. "),
        ]

        scenes = []
        for i, (title, emotion, shot, location, lead) in enumerate(beats, 1):
            chars = ["Tara"]
            if i in (3, 5, 6, 7, 8):
                chars.append("Guardian")
            if i in (4, 5):
                chars.append("Shadow")
            scenes.append({
                "scene_number": i,
                "title": title,
                "description": lead + story[:500],
                "story_context": story[:700],
                "location": location,
                "characters": chars,
                "emotion": emotion,
                "visual_direction": "Cinematic stylized 3D character acting with consistent locked identities, natural poses, readable emotion and story-focused composition.",
                "camera_direction": shot + " cinematic character shot with gentle movement.",
                "props": ["blue star"] if i in (2, 7, 8) else [],
                "estimated_duration_seconds": 2,
                "status": "PLANNED",
                "progress": 0,
            })

        return {
            "title": "Aadwik Phase 23 Cinematic Production",
            "story": story,
            "scenes": scenes,
            "phase": 23,
            "visual_pipeline": "character_identity_locked_cinematic_3d",
        }

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _resolution(aspect_ratio: str):
        if aspect_ratio == "9:16":
            return 360, 640
        if aspect_ratio == "1:1":
            return 512, 512
        return 640, 360

    @staticmethod
    def _find_png_frames(frames_dir: Path):
        files = [
            p for p in frames_dir.rglob("*.png")
            if p.is_file()
        ]

        def key_fn(p: Path):
            nums = []
            current = ""
            for ch in p.stem:
                if ch.isdigit():
                    current += ch
                elif current:
                    nums.append(int(current))
                    current = ""
            if current:
                nums.append(int(current))
            return (tuple(nums), p.name.lower())

        files.sort(key=key_fn)
        return files

    def _validate(self):
        if not BLENDER_EXE.exists():
            raise FileNotFoundError(
                f"Blender not found: {BLENDER_EXE}"
            )

        if not FFMPEG_EXE.exists():
            raise FileNotFoundError(
                f"FFmpeg not found: {FFMPEG_EXE}"
            )

        if not SCENE_SCRIPT.exists():
            raise FileNotFoundError(
                f"Scene script not found: {SCENE_SCRIPT}"
            )

    def _probe_video(self, path: Path):
        """
        Use ffprobe if available next to FFmpeg. If ffprobe is unavailable,
        fall back to ffmpeg's output parsing.
        """
        ffprobe = FFMPEG_EXE.with_name("ffprobe.exe")

        if ffprobe.exists():
            cmd = [
                str(ffprobe),
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-count_frames",
                "-show_entries",
                "stream=nb_read_frames,r_frame_rate,duration",
                "-of",
                "default=noprint_wrappers=1:nokey=0",
                str(path),
            ]

            r = subprocess.run(
                cmd,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            if r.returncode == 0:
                values = {}
                for line in r.stdout.splitlines():
                    if "=" in line:
                        k, v = line.split("=", 1)
                        values[k.strip()] = v.strip()

                frames = int(values.get("nb_read_frames", "0"))

                rate = values.get("r_frame_rate", "0/1")
                if "/" in rate:
                    a, b = rate.split("/", 1)
                    fps = float(a) / float(b) if float(b) else 0.0
                else:
                    fps = float(rate or 0)

                duration = float(values.get("duration", "0") or 0)

                return frames, fps, duration

        # Fallback: ask ffmpeg for stream information.
        cmd = [
            str(FFMPEG_EXE),
            "-i",
            str(path),
        ]

        r = subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        text = r.stderr

        fps = 0.0
        duration = 0.0

        for line in text.splitlines():
            if "Duration:" in line:
                try:
                    value = line.split("Duration:", 1)[1].split(",", 1)[0].strip()
                    hh, mm, ss = value.split(":")
                    duration = (
                        float(hh) * 3600
                        + float(mm) * 60
                        + float(ss)
                    )
                except Exception:
                    pass

            if " fps" in line and "Video:" in line:
                try:
                    part = line.split(",", 1)[-1]
                    token = part.strip().split()[0]
                    fps = float(token)
                except Exception:
                    pass

        # Conservative fallback; final frame-count verification is best when
        # ffprobe exists, which is included in normal FFmpeg GPL builds.
        frames = int(round(duration * fps)) if fps > 0 else 0

        return frames, fps, duration

    @staticmethod
    def _create_audio(path: Path, duration: float, sample_rate=44100):
        total = max(1, int(duration * sample_rate))

        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)

            amplitude = 2500
            chunk = 4096

            for start in range(0, total, chunk):
                end = min(total, start + chunk)
                data = bytearray()

                for n in range(start, end):
                    t = n / sample_rate

                    # Soft cinematic underwater pad.
                    signal = (
                        0.52 * math.sin(2 * math.pi * 110.0 * t)
                        + 0.24 * math.sin(2 * math.pi * 165.0 * t)
                        + 0.10 * math.sin(2 * math.pi * 220.0 * t)
                    )

                    pulse = (
                        0.70
                        + 0.30
                        * math.sin(2 * math.pi * 0.08 * t)
                    )

                    fade_in = min(1.0, t / 1.2)
                    fade_out = min(
                        1.0,
                        max(0.0, (duration - t) / 1.2),
                    )

                    s = int(
                        amplitude
                        * signal
                        * pulse
                        * fade_in
                        * fade_out
                    )

                    s = max(-32768, min(32767, s))

                    data += int(s).to_bytes(
                        2,
                        "little",
                        signed=True,
                    )

                    data += int(s * 0.92).to_bytes(
                        2,
                        "little",
                        signed=True,
                    )

                wav.writeframes(data)


# Compatibility aliases
local_video_provider = LocalVideoProvider()
video_provider = local_video_provider
VideoProvider = LocalVideoProvider
