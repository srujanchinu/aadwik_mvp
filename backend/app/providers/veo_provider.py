import os
import time
from pathlib import Path

from google import genai
from google.genai import types


class VeoProvider:
    """
    Aadwik Veo video generation provider.

    Generates a real video from the Aadwik movie prompt
    and saves the MP4 into the backend/generated folder.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Set your real Gemini API key before starting Aadwik."
            )

        if api_key == "PASTE_YOUR_REAL_GEMINI_API_KEY_HERE":
            raise RuntimeError(
                "GEMINI_API_KEY is still the placeholder text. "
                "Replace it with your real Gemini API key."
            )

        print(
            "[AADWIK VEO] GEMINI_API_KEY detected."
        )

        self.client = genai.Client(
            api_key=api_key,
        )

    def generate_video(
        self,
        prompt: str,
        output_path: Path,
        aspect_ratio: str = "16:9",
    ) -> Path:

        try:

            if not prompt or not prompt.strip():
                raise RuntimeError(
                    "Cannot generate video because the Aadwik prompt is empty."
                )

            output_path = Path(output_path)

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            if aspect_ratio not in [
                "16:9",
                "9:16",
            ]:
                aspect_ratio = "16:9"

            print()
            print("=" * 60)
            print("[AADWIK VEO] STARTING REAL AI VIDEO GENERATION")
            print(f"[AADWIK VEO] Model: veo-3.1-generate-preview")
            print(f"[AADWIK VEO] Aspect ratio: {aspect_ratio}")
            print(f"[AADWIK VEO] Output: {output_path}")
            print("=" * 60)

            # ==================================================
            # START VEO GENERATION
            # ==================================================

            operation = self.client.models.generate_videos(
                model="veo-3.1-generate-preview",
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio=aspect_ratio,
                    number_of_videos=1,
                ),
            )

            print(
                "[AADWIK VEO] Google accepted the generation request."
            )

            # ==================================================
            # WAIT FOR VEO
            # ==================================================

            while not operation.done:

                print(
                    "[AADWIK VEO] Waiting for Google Veo generation..."
                )

                time.sleep(10)

                operation = self.client.operations.get(
                    operation,
                )

            print(
                "[AADWIK VEO] Generation operation completed."
            )

            # ==================================================
            # CHECK GOOGLE OPERATION ERROR
            # ==================================================

            if getattr(operation, "error", None):

                error_message = str(
                    operation.error
                )

                print(
                    "[AADWIK VEO] GOOGLE OPERATION ERROR:"
                )

                print(
                    error_message
                )

                raise RuntimeError(
                    f"Google Veo generation failed: {error_message}"
                )

            # ==================================================
            # CHECK RESPONSE
            # ==================================================

            if not operation.response:

                print(
                    "[AADWIK VEO] FULL OPERATION:"
                )

                print(
                    operation
                )

                raise RuntimeError(
                    "Veo generation finished but returned no response."
                )

            generated_videos = getattr(
                operation.response,
                "generated_videos",
                None,
            )

            if not generated_videos:

                print(
                    "[AADWIK VEO] RESPONSE:"
                )

                print(
                    operation.response
                )

                raise RuntimeError(
                    "Veo generation finished but no video was returned."
                )

            generated_video = (
                generated_videos[0]
            )

            video_file = getattr(
                generated_video,
                "video",
                None,
            )

            if not video_file:

                raise RuntimeError(
                    "Veo returned an empty video result."
                )

            # ==================================================
            # DOWNLOAD MP4
            # ==================================================

            print(
                "[AADWIK VEO] Downloading generated MP4..."
            )

            self.client.files.download(
                file=video_file,
                destination=str(
                    output_path,
                ),
            )

            if not output_path.exists():

                raise RuntimeError(
                    "Veo download completed but the MP4 file was not found."
                )

            if output_path.stat().st_size == 0:

                raise RuntimeError(
                    "Veo created an empty MP4 file."
                )

            print()
            print("=" * 60)
            print("[AADWIK VEO] VIDEO SUCCESSFULLY SAVED")
            print(f"[AADWIK VEO] File: {output_path}")
            print(
                f"[AADWIK VEO] Size: "
                f"{output_path.stat().st_size} bytes"
            )
            print("=" * 60)
            print()

            return output_path

        except Exception as exc:

            print()
            print("=" * 60)
            print("[AADWIK VEO] GENERATION FAILED")
            print(
                f"[AADWIK VEO] Error type: "
                f"{type(exc).__name__}"
            )
            print(
                f"[AADWIK VEO] Error: "
                f"{exc}"
            )
            print("=" * 60)
            print()

            raise RuntimeError(
                f"VeoProvider error: {type(exc).__name__}: {exc}"
            ) from exc