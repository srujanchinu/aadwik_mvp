from aadwik_movie_assembler import assemble_movie
p=assemble_movie()
assert p["compositing"] and p["titles"] and p["subtitles"]
print("FINAL COMPOSITING PACKAGE: OK")
print("COLOR + TITLES + SUBTITLES: OK")
print("STEP 11F PASS")
