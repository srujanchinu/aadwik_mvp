
from app.providers.blender_production_adapter import run_blender_job

job=r"blender_job_test.json"
script=r"C:\Users\olga_Ashok3\aadwik_mvp\backend\app\providers\aadwik_story_aware_scene.py"
out=r"blender_step7_test"

result=run_blender_job(job,script,out,shot_limit=2)
print(result["stdout_tail"])
print("\nSTEP 7 PASS")
