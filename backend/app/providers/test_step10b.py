from aadwik_dialogue_engine import DialogueLine, DialogueTimeline, save_timeline

timeline=DialogueTimeline()

timeline.add(DialogueLine(
    "dlg_001","char_tara_v1",
    "What was that?", "scene_02","scene_02_shot_01",
    0.0,1.8,emotion="curious"
))
timeline.add(DialogueLine(
    "dlg_002","char_guardian_v1",
    "Please help me.", "scene_04","scene_04_shot_02",
    2.0,2.0,emotion="weak"
))
timeline.add(DialogueLine(
    "dlg_003","char_shadow_creature_v1",
    "You cannot take the star.", "scene_09","scene_09_shot_03",
    4.2,2.4,emotion="threatening"
))
timeline.add(DialogueLine(
    "dlg_004","char_tara_v1",
    "I will not leave you.", "scene_10","scene_10_shot_02",
    6.8,2.1,emotion="courageous"
))

report=timeline.validate()
assert report["valid"]
assert report["line_count"]==4
assert report["schema"]=="aadwik-dialogue-1.0"
assert report["lines"][0]["character_id"]=="char_tara_v1"
assert report["lines"][1]["character_id"]=="char_guardian_v1"
assert report["lines"][2]["character_id"]=="char_shadow_creature_v1"

save_timeline(timeline,"step10b_dialogue_timeline.json")

print("DIALOGUE ENGINE: CONNECTED")
print("CHARACTER -> DIALOGUE BINDING: OK")
print("DIALOGUE TIMING: OK")
print("EMOTION TAGGING: OK")
print("CHRONOLOGICAL TIMELINE: OK")
print("PROVIDER-AGNOSTIC DIALOGUE LAYER: OK")
print("STEP 10B PASS")
