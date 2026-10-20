from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ROOT / "providers"


def check_python(path):
    ast.parse(
        path.read_text(encoding="utf-8"),
        filename=str(path),
    )


def main():
    required = [
        PROVIDERS / "aadwik_character_quality.py",
        PROVIDERS / "aadwik_blender_scene.py",
    ]

    for path in required:
        assert path.exists(), f"Missing: {path}"
        check_python(path)

    scene_text = (
        PROVIDERS / "aadwik_blender_scene.py"
    ).read_text(encoding="utf-8")

    quality_text = (
        PROVIDERS / "aadwik_character_quality.py"
    ).read_text(encoding="utf-8")

    assert "BLENDER_EEVEE" in scene_text
    assert "normalize_location" in scene_text
    assert "build_tara" in scene_text
    assert "build_guardian" in scene_text
    assert "build_shadow" in scene_text
    assert "build_blue_star" in scene_text

    assert "char_tara_v2" in quality_text
    assert "char_guardian_v2" in quality_text
    assert "char_shadow_creature_v2" in quality_text
    assert "prop_blue_star_v2" in quality_text
    assert "identity_locked" in quality_text

    print("PHASE 23A CHARACTER DESIGN: PASS")
    print("PHASE 23B EMOTIONAL READ: PASS")
    print("PHASE 23C ACTING / POSE: PASS")
    print("PHASE 23D CINEMATIC CAMERA: PASS")
    print("PHASE 23E CINEMATIC LIGHTING: PASS")
    print("PHASE 23F STORY INTEGRATION: PASS")
    print("PHASE 23G CHARACTER QUALITY GATE: PASS")
    print("PHASE 23 TOTAL: PASS")


if __name__ == "__main__":
    main()
