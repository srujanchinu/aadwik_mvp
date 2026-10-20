from pathlib import Path

def test_provider_and_scene_present():
    base = Path(__file__).parents[1] / 'app' / 'renderer'
    assert (base / 'local_video_provider.py').exists()
    assert (base / 'aadwik_animation_scene.py').exists()
