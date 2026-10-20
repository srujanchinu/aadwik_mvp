import unittest
from app.engines.creative_intelligence import (
    create_character_lock, create_world_lock, lock_story_bible,
    validate_story_continuity, repair_recommendations
)

class MasterBatch3Tests(unittest.TestCase):
    def test_character_lock(self):
        x=create_character_lock({"character_id":"tara","name":"Tara"})
        self.assertTrue(x["identity_locked"])
        self.assertEqual(x["design_version"],"v1")

    def test_world_lock(self):
        x=create_world_lock({"world_id":"forest","name":"Moonlit Forest"})
        self.assertTrue(x["identity_locked"])
        self.assertEqual(x["visual_style"],"cinematic_stylized_3d")

    def test_story_bible_lock(self):
        b=lock_story_bible({
            "title":"Test",
            "characters":[{"character_id":"tara","name":"Tara"}],
            "worlds":[{"world_id":"forest","name":"Forest"}]
        })
        self.assertTrue(b["locked"])
        self.assertTrue(b["characters"][0]["identity_locked"])

    def test_continuity_pass(self):
        bible={"characters":[{"character_id":"tara"}],"worlds":[{"world_id":"forest"}]}
        scenes=[{"scene_number":1,"characters":["tara"],"locations":["forest"]}]
        shots=[{"shot_id":"s1","scene_number":1,"characters":["tara"],"locations":["forest"]}]
        r=validate_story_continuity(bible,scenes,shots)
        self.assertTrue(r["passed"])
        self.assertEqual(r["issues"],[])

    def test_continuity_fail_and_repair(self):
        bible={"characters":[{"character_id":"tara"}],"worlds":[{"world_id":"forest"}]}
        scenes=[{"scene_number":1,"characters":["unknown"],"locations":["forest"]}]
        shots=[]
        r=validate_story_continuity(bible,scenes,shots)
        self.assertFalse(r["passed"])
        self.assertTrue(repair_recommendations(r))

if __name__=="__main__":
    unittest.main()
