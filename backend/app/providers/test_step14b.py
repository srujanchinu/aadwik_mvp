from aadwik_translation_engine import translate_story_package
story = {"title":"The Last Star","scenes":[{"scene":i} for i in range(14)]}
out = translate_story_package(story, "en", "te")
assert out["translation_status"] == "READY_FOR_PROVIDER"
assert len(out["scenes"]) == 14
print("STORY TRANSLATION PIPELINE: OK")
print("14 SCENES PRESERVED: OK")
print("STEP 14B PASS")
