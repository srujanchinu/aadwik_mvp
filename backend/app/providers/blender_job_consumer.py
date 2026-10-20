
from __future__ import annotations
from pathlib import Path
import json
import subprocess
from typing import Any, Dict

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

def load_blender_job(path) -> Dict[str,Any]:
    path=Path(path)
    return json.loads(path.read_text(encoding="utf-8"))

def validate_blender_job(job):
    if job.get("schema_version") != "aadwik-blender-job-1.0":
        raise ValueError("Unsupported Blender job schema.")
    if not job.get("shots"):
        raise ValueError("Blender job contains no shots.")
    for shot in job["shots"]:
        for field in ("shot_id","location","characters","story_context","framing","lens","camera_movement"):
            if field not in shot:
                raise ValueError(f"{shot.get('shot_id','unknown')}: missing {field}")
    return True

def write_blender_input(job:Dict[str,Any], path) -> str:
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(job,indent=2,ensure_ascii=False),encoding="utf-8")
    return str(path)

def run_blender_job(job_path, blender_script, output_dir, shot_limit=2):
    job=load_blender_job(job_path)
    validate_blender_job(job)
    output=Path(output_dir)
    output.mkdir(parents=True,exist_ok=True)
    cmd=[BLENDER_EXE,"--background","--python",str(blender_script),"--",
         str(job_path),str(output),str(int(shot_limit))]
    result=subprocess.run(cmd,capture_output=True,text=True)
    if result.returncode != 0:
        raise RuntimeError("Blender job failed:\n"+result.stdout+"\n"+result.stderr)
    return {"returncode":result.returncode,"output_dir":str(output),
            "stdout_tail":result.stdout[-4000:],"stderr_tail":result.stderr[-2000:]}
