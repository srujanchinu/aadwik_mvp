from aadwik_localization_engine import SUPPORTED_LANGUAGES, build_localization_job
job = build_localization_job("the_last_star", "en", ["te","hi","ta","kn","ml","mr","bn","gu","pa","ur","or","as"])
assert len(SUPPORTED_LANGUAGES) == 13
assert job["status"] == "READY"
print("LANGUAGE SYSTEM: OK")
print("13-LANGUAGE INITIAL PACK: OK")
print("STEP 14A PASS")
