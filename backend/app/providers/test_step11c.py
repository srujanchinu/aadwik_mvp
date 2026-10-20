from aadwik_av_sync import validate_av
r=validate_av(20,[("dialogue",1,2),("music",0,18),("sfx",5,1),("ambience",0,20)])
assert r["valid"]
print("VIDEO + DIALOGUE SYNC: OK")
print("VIDEO + MUSIC SYNC: OK")
print("VIDEO + SFX SYNC: OK")
print("VIDEO + AMBIENCE SYNC: OK")
print("STEP 11C PASS")
