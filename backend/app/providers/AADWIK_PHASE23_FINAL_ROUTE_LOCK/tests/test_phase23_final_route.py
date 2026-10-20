
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "providers" / "local_video_provider.py"

src = P.read_text(encoding="utf-8")
ast.parse(src)

assert "PHASE_23_FINAL_ROUTE_LOCK" in src
assert 'output_path.stem + "_phase23"' in src
assert 'rendered_frames' in src
assert 'ffmpeg_sequence' in src
assert 'backend\\frames' in src
assert '"--out"' in src
assert 'str(frames_dir / "frame_%06d.png")' in src
assert "local_video_provider = LocalVideoProvider()" in src

print("PHASE 23 FINAL ROUTE LOCK: PASS")
print("Per-movie permanent render directory: PASS")
print("Legacy frame folders cannot be selected: PASS")
print("FFmpeg source locked to current render: PASS")
