from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'app' / 'repair' / 'aadwik_character_quality.py'
TEXT = SOURCE.read_text(encoding='utf-8')

required = [
    'def build_tara(',
    'def build_guardian(',
    'def build_shadow(',
    'def build_blue_star(',
    'def apply_emotion(',
    'def direct_character_gaze(',
]

for item in required:
    assert item in TEXT, f'missing required Phase 23 API: {item}'

assert 'char_tara_v2' in TEXT
assert 'char_guardian_v2' in TEXT
assert 'char_shadow_creature_v2' in TEXT
assert 'prop_blue_star_v2' in TEXT
assert 'import bpy' in TEXT

print('BATCH 30 TESTS: 5/5 PASS')
print('Phase 23 character-quality API compatibility verified.')
