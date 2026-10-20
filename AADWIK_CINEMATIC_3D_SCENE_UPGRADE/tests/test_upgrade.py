from pathlib import Path
def test_scene_and_provider_exist():
    assert Path('app/renderer/aadwik_animation_scene.py').exists()
    assert Path('app/renderer/local_video_provider.py').exists()
