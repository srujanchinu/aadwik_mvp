from aadwik_final_movie_assembly import assemble_final_movie

sequence = {"shot_count":41}
audio = {"shot_count":41}
timeline = {"clips":[{"shot":i} for i in range(41)]}
qc = {"publishing_gate":True}

out = assemble_final_movie(sequence, audio, timeline, qc)
assert out["status"] == "ASSEMBLED"
assert out["export_ready"] is True
assert out["qc_gate"] == "OPEN"
print("3D SEQUENCE + AUDIO + TIMELINE: CONNECTED")
print("FINAL MOVIE ASSEMBLY: OK")
print("EXPORT READY: OK")
print("STEP 13F PASS")
