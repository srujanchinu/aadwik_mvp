
from app.providers.story_visual_planner import analyze_story
from app.providers.continuity_locks import apply_locks
from app.providers.cinematic_shot_planner import build_shot_plan
from app.providers.production_payload import build_production_payload, save_production_payload

story="""On the night of a village festival, a curious 12-year-old girl named Tara sees a strange blue star fall from the sky and disappear into the nearby forest. She follows its glowing trail and discovers a tiny injured creature hiding beneath an ancient tree. The creature is actually a young guardian whose magical star has been stolen by a shadow creature. Tara decides to help. Together they journey through the moonlit forest, cross a glowing river, and enter an abandoned stone temple. Inside, Tara must face the shadow creature—not with a weapon, but with courage and compassion. When she returns the star to the guardian, the entire forest comes alive with light. At sunrise, Tara returns home and discovers that one tiny star is still glowing in her hand."""

plan=analyze_story(story,title="The Last Star")
plan=apply_locks(plan)
plan=build_shot_plan(plan)
payload=build_production_payload(plan)

print("\n=== PRODUCTION PAYLOAD ===")
print(payload["schema_version"])
print("Scenes:",len(payload["scenes"]))
print("Shots:",sum(len(s["shots"]) for s in payload["scenes"]))

print("\n=== FIRST SHOT ===")
print(payload["scenes"][0]["shots"][0])

print("\n=== SHOT 9 CHECK ===")
print(payload["scenes"][8]["shots"][0])

out=save_production_payload(plan,r"production_test.json")
print("\nSaved:",out)
