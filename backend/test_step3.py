from app.providers.story_visual_planner import analyze_story
from app.providers.continuity_locks import apply_locks

story = """On the night of a village festival, a curious 12-year-old girl named Tara sees a strange blue star fall from the sky and disappear into the nearby forest. She follows its glowing trail and discovers a tiny injured creature hiding beneath an ancient tree. The creature is actually a young guardian whose magical star has been stolen by a shadow creature. Tara decides to help. Together they journey through the moonlit forest, cross a glowing river, and enter an abandoned stone temple. Inside, Tara must face the shadow creature—not with a weapon, but with courage and compassion. When she returns the star to the guardian, the entire forest comes alive with light. At sunrise, Tara returns home and discovers that one tiny star is still glowing in her hand."""

plan = analyze_story(story, title="The Last Star")
plan = apply_locks(plan)

print("\n=== PRODUCTION SUMMARY ===")
print(plan["production_summary"])

print("\n=== CHARACTER LOCK ===")
for character in plan["character_lock"]["characters"]:
    print(
        character["id"],
        "->",
        character["name"],
        "|",
        character["type"],
        "|",
        character["role"]
    )

print("\n=== WORLD LOCK ===")
for world in plan["world_lock"]["locations"]:
    print(world["id"], "->", world["name"])

print("\n=== PROP LOCK ===")
for prop in plan["prop_lock"]["props"]:
    print(prop["id"], "->", prop["name"])

print("\n=== SCENE 9 ===")
scene = plan["scenes"][8]

print("Title:", scene["title"])
print("Characters:", scene["characters"])
print("Location:", scene["location"])
print("Props:", scene["props"])

print("\n=== CONTINUITY ===")
print(plan["production_summary"]["continuity_locked"])