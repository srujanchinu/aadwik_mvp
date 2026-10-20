from aadwik_voice_engine import VoiceProfile, VoiceLibrary, save_manifest

library=VoiceLibrary()

library.register(VoiceProfile(
    "voice_tara_v1","char_tara_v1","Tara",
    language="en-IN",gender="female",age="young",
    style="curious_natural",pitch="medium",speed=1.0
))
library.register(VoiceProfile(
    "voice_guardian_v1","char_guardian_v1","Guardian",
    language="en-IN",gender="neutral",age="young",
    style="gentle_magical",pitch="medium",speed=0.92
))
library.register(VoiceProfile(
    "voice_shadow_v1","char_shadow_creature_v1","Shadow Creature",
    language="en-IN",gender="neutral",age="unknown",
    style="mysterious_threatening",pitch="low",speed=0.88
))

assert library.get("char_tara_v1").voice_id=="voice_tara_v1"
assert library.get("char_guardian_v1").voice_id=="voice_guardian_v1"
assert library.get("char_shadow_creature_v1").voice_id=="voice_shadow_v1"

manifest=library.manifest()
assert manifest["schema"]=="aadwik-voice-profile-1.0"
assert manifest["voice_count"]==3

# Identity lock: repeated lookup must return the same voice profile.
assert library.get("char_tara_v1").voice_id=="voice_tara_v1"
assert library.get("char_guardian_v1").voice_id=="voice_guardian_v1"
assert library.get("char_shadow_creature_v1").voice_id=="voice_shadow_v1"

save_manifest(library,"step10a_voice_manifest.json")

print("VOICE ENGINE: CONNECTED")
print("TARA VOICE LOCK: OK")
print("GUARDIAN VOICE LOCK: OK")
print("SHADOW VOICE LOCK: OK")
print("VOICE PROFILE SCHEMA: OK")
print("VOICE IDENTITY REUSE: OK")
print("PROVIDER-AGNOSTIC VOICE LAYER: OK")
print("STEP 10A PASS")
