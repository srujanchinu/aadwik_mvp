import asyncio
import re
import shutil
from pathlib import Path

import edge_tts

FFMPEG_EXE = Path(
    r"C:\ffmpeg-n9.0-latest-win64-gpl-9.0\bin\ffmpeg.exe"
)

VOICES = {
    "english": "en-IN-NeerjaNeural",
    "telugu": "te-IN-ShrutiNeural",
}


def split_story(text: str, max_chars: int = 2500) -> list[str]:
    """Split a complete story at sentence boundaries where possible."""
    text = re.sub(r"\s+", " ", (text or "")).strip()
    if not text:
        raise ValueError("Narration text is empty.")

    sentences = re.split(r"(?<=[.!?।])\s+", text)
    chunks = []
    current = ""

    for sentence in sentences:
        while len(sentence) > max_chars:
            if current:
                chunks.append(current)
                current = ""

            cut = sentence.rfind(" ", 0, max_chars + 1)
            if cut <= 0:
                cut = max_chars

            chunks.append(sentence[:cut].strip())
            sentence = sentence[cut:].strip()

        if not sentence:
            continue

        candidate = f"{current} {sentence}".strip()
        if len(candidate) > max_chars and current:
            chunks.append(current)
            current = sentence
        else:
            current = candidate

    if current:
        chunks.append(current)

    if not chunks or "".join(chunks).strip() == "":
        raise ValueError("No narration chunks were created.")

    return chunks


async def _generate_chunk(text: str, voice: str, destination: Path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(destination))

    if not destination.exists() or destination.stat().st_size == 0:
        raise RuntimeError(f"TTS generated an empty chunk: {destination.name}")


async def generate_narration(
    text: str,
    output_path: str | Path,
    language: str = "English",
    voice: str | None = None,
) -> str:
    """Generate narration for the entire supplied story and validate the audio."""
    if not FFMPEG_EXE.is_file():
        raise FileNotFoundError(f"FFmpeg not found: {FFMPEG_EXE}")

    selected_voice = voice or VOICES.get(
        language.strip().lower(), "en-IN-NeerjaNeural"
    )
    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    work = output.parent / f"{output.stem}_narration_chunks"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    chunks = split_story(text)
    concat_file = work / "concat.txt"

    try:
        entries = []
        for index, chunk in enumerate(chunks, start=1):
            chunk_path = work / f"chunk_{index:04d}.mp3"
            await _generate_chunk(chunk, selected_voice, chunk_path)
            entries.append(f"file '{chunk_path.as_posix()}'")

        concat_file.write_text(
            "\n".join(entries) + "\n", encoding="utf-8"
        )

        import subprocess

        command = [
            str(FFMPEG_EXE), "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-vn", "-c:a", "libmp3lame", "-q:a", "3",
            str(output),
        ]
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=900
        )
        if result.returncode != 0:
            raise RuntimeError(
                "FFmpeg narration assembly failed:\n" + result.stderr[-4000:]
            )

        if not output.exists() or output.stat().st_size == 0:
            raise RuntimeError("Final narration file is missing or empty.")

        print(
            f"[AADWIK NARRATION] chunks={len(chunks)} "
            f"voice={selected_voice} file={output}"
        )
        return str(output)

    except Exception:
        if output.exists():
            output.unlink()
        raise
