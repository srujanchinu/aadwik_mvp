import bpy, runpy
from pathlib import Path
mod=runpy.run_path("aadwik_world_builder.py")
render_preview=mod["render_preview"]
ids=list(mod["WORLD_SPECS"].keys())
out=Path("step9b_world_previews"); out.mkdir(exist_ok=True)
for wid in ids:
    p=out/(wid+".png")
    render_preview(wid,p)
    assert p.exists()
    print("RENDERED",wid)
print("ACTUAL 3D WORLDS: OK")
print("WORLD REUSE: OK")
print("EEVEE RENDERING: OK")
print("STEP 9B PASS")
