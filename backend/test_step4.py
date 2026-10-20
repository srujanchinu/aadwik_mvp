
from app.providers.story_visual_planner import analyze_story
from app.providers.continuity_locks import apply_locks
from app.providers.cinematic_shot_planner import build_shot_plan

story="""On the night of a village festival, a curious 12-year-old girl named Tara sees a strange blue star fall from the sky and disappear into the nearby forest. She follows its glowing trail and discovers a tiny injured creature hiding beneath an ancient tree. The creature is actually a young guardian whose magical star has been stolen by a shadow creature. Tara decides to help. Together they journey through the moonlit forest, cross a glowing river, and enter an abandoned stone temple. Inside, Tara must face the shadow creature—not with a weapon, but with courage and compassion. When she returns the star to the guardian, the entire forest comes alive with light. At sunrise, Tara returns home and discovers that one tiny star is still glowing in her hand."""

plan=apply_locks(analyze_story(story,title="The Last Star"))
plan=build_shot_plan(plan)

print("\n=== SHOT PLAN SUMMARY ===")
print(plan["shot_plan"])
print("\n=== SCENE 2 SHOTS ===")
for s in plan["scenes"][1]["shots"]:
    print(s["shot_id"], "|", s["shot_type"], "|", s["framing"], "|", s["lens"], "|", s["camera_movement"])
print("\n=== SCENE 9 SHOT ===")
print(plan["scenes"][8]["shots"][0])
print("\n=== STATUS ===")
print(plan["production_summary"])
