from __future__ import annotations

from pathlib import Path
import json
import subprocess
from typing import Any, Dict


BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


REQUIRED_SHOT_FIELDS = [
    "shot_id",
    "scene_number",
    "shot_number",
    "framing",
    "lens",
    "camera_movement",
    "location",
    "characters",
    "props",
    "story_context",
]


def load_blender_job(path) -> Dict[str, Any]:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Production Blender job not found: {path}"
        )

    return json.loads(
        path.read_text(encoding="utf-8")
    )


def validate_blender_job(job: Dict[str, Any]) -> bool:

    if job.get("schema_version") != "aadwik-blender-job-1.0":
        raise ValueError(
            f"Unsupported Blender job schema: "
            f"{job.get('schema_version')}"
        )

    if not job.get("shots"):
        raise ValueError(
            "Blender job contains no shots."
        )

    for shot in job["shots"]:

        shot_id = shot.get(
            "shot_id",
            "unknown"
        )

        for field in REQUIRED_SHOT_FIELDS:

            if field not in shot:
                raise ValueError(
                    f"{shot_id}: missing field '{field}'"
                )

        continuity = shot.get(
            "continuity",
            {}
        )

        if continuity.get(
            "character_lock"
        ) is not True:
            raise ValueError(
                f"{shot_id}: character lock missing"
            )

        if continuity.get(
            "world_lock"
        ) is not True:
            raise ValueError(
                f"{shot_id}: world lock missing"
            )

        if continuity.get(
            "prop_lock"
        ) is not True:
            raise ValueError(
                f"{shot_id}: prop lock missing"
            )

    return True


def write_blender_input(
    job: Dict[str, Any],
    path
) -> str:

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_text(
        json.dumps(
            job,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    return str(path)


def run_blender_job(
    job_path,
    blender_script,
    output_dir,
    shot_limit=2
):

    job = load_blender_job(
        job_path
    )

    validate_blender_job(
        job
    )

    output = Path(
        output_dir
    )

    output.mkdir(
        parents=True,
        exist_ok=True
    )

    blender_script = Path(
        blender_script
    )

    if not blender_script.exists():
        raise FileNotFoundError(
            f"Blender scene script not found: "
            f"{blender_script}"
        )

    blender_exe = Path(
        BLENDER_EXE
    )

    if not blender_exe.exists():
        raise FileNotFoundError(
            f"Blender executable not found: "
            f"{blender_exe}"
        )

    shot_limit = int(
        shot_limit
    )

    if shot_limit < 1:
        raise ValueError(
            "shot_limit must be at least 1"
        )

    shot_limit = min(
        shot_limit,
        len(job["shots"])
    )

    command = [
        str(blender_exe),

        "--background",

        "--python",
        str(blender_script),

        "--",

        str(Path(job_path).resolve()),

        str(output.resolve()),

        str(shot_limit),
    ]

    print(
        "\n=== BLENDER COMMAND ==="
    )

    print(
        " ".join(
            f'"{x}"'
            if " " in str(x)
            else str(x)
            for x in command
        )
    )

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        raise RuntimeError(
            "\nBlender job failed.\n\n"
            "STDOUT:\n"
            + result.stdout
            + "\n\nSTDERR:\n"
            + result.stderr
        )

    return {
        "returncode":
            result.returncode,

        "output_dir":
            str(output),

        "shots_rendered":
            shot_limit,

        "stdout_tail":
            result.stdout[-4000:],

        "stderr_tail":
            result.stderr[-2000:],
    }


# Compatibility aliases

load_job = load_blender_job

validate_job = validate_blender_job

run_job = run_blender_job