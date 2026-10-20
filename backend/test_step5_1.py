
from app.providers.story_visual_planner import analyze_story
from app.providers.continuity_locks import apply_locks
from app.providers.cinematic_shot_planner import build_shot_plan
from app.providers.production_data_cleanup import clean_production_plan

story="""On the night of a village festival, a curious 12-year-old girl named Tara sees a strange blue star fall from the sky and disappear into the nearby forest. She follows its glowing trail and discovers a tiny injured creature hiding beneath an ancient tree. The creature is actually a young guardian whose magical star has been stolen by a shadow creature. Tara decides to help. Together they journey through the moonlit forest, cross a glowing river, and enter an abandoned stone temple. Inside, Tara must face the shadow creature—not with a weapon, but with courage and compassion. When she returns the star to the guardian, the entire forest comes alive with light. At sunrise, Tara returns home and discovers that one tiny star is still glowing in her hand."""

plan=analyze_story(story,title="The Last Star")
plan=apply_locks(plan)
plan=build_shot_plan(plan)
plan=clean_production_plan(plan)

print("\n=== CLEAN SUMMARY ===")
print(plan["production_summary"])

print("\n=== CHARACTERS ===")
print([(c["id"],c["name"]) for c in plan["character_lock"]["characters"]])

print("\n=== SCENE 9 ===")
s=plan["scenes"][8]
print("Title:",s["title"])
print("Characters:",s["characters"])
print("Context:",s["story_context"])

print("\n=== SCENE 2 ===")
print(plan["scenes"][1]["story_context"])

assert len(plan["character_lock"]["characters"]) == 3
assert s["story_context"].startswith("Inside the temple")
assert plan["production_summary"]["exact_contexts"] == 14
print("\nSTEP 5.1 PASS")
