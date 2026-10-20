
from app.providers.blender_production_adapter import load_blender_job, validate_blender_job, run_blender_job

job_path=r"blender_job_test.json"
script=r"C:\Users\olga_Ashok3\aadwik_mvp\backend\app\providers\aadwik_blender_job_scene.py"
out=r"blender_step6b_test"

job=load_blender_job(job_path)
print("JOB:",job["title"])
print("VALID:",validate_blender_job(job))
print("SHOTS:",len(job["shots"]))

result=run_blender_job(job_path,script,out,shot_limit=2)
print(result["stdout_tail"])
print("\nSTEP 6B PASS")
