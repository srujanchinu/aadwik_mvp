
from app.providers.production_payload import build_production_payload
from app.providers.story_visual_planner import analyze_story
from app.providers.continuity_locks import apply_locks
from app.providers.cinematic_shot_planner import build_shot_plan
from app.providers.production_data_cleanup import clean_production_plan
from app.providers.blender_production_adapter import validate_payload, build_blender_job, save_blender_job

story="""On the night of a village festival, a curious 12-year-old girl named Tara sees a strange blue star fall from the sky and disappear into the nearby forest. She follows its glowing trail and discovers a tiny injured creature hiding beneath an ancient tree. The creature is actually a young guardian whose magical star has been stolen by a shadow creature. Tara decides to help. Together they journey through the moonlit forest, cross a glowing river, and enter an abandoned stone temple. Inside, Tara must face the shadow creature—not with a weapon, but with courage and compassion. When she returns the star to the guardian, the entire forest comes alive with light. At sunrise, Tara returns home and discovers that one tiny star is still glowing in her hand."""

plan=analyze_story(story,title="The Last Star")
plan=apply_locks(plan)
plan=build_shot_plan(plan)
plan=clean_production_plan(plan)
payload=build_production_payload(plan)

check=validate_payload(payload)
print("\n=== PAYLOAD VALIDATION ===")
print(check)

job=build_blender_job(payload)
print("\n=== BLENDER JOB ===")
print(job["schema_version"])
print(job["counts"])
print("\n=== FIRST BLENDER SHOT ===")
print(job["shots"][0])
print("\n=== SHOT 9 ===")
print(next(x for x in job["shots"] if x["shot_id"]=="scene_09_shot_01"))

print("\nSaved:",save_blender_job(payload,"blender_job_test.json"))
print("\nSTEP 6A PASS")
