import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.creative.story_bible import StoryBible, CanonGuard
from app.creative.story_continuity import StoryContinuityTracker
from app.creative.scene_intent import SceneIntent, validate_scene_intent
from app.creative.quality_review import CreativeQualityReviewer

class TestBatch11(unittest.TestCase):
    def make_bible(self):
        bible = StoryBible("Blue Star", "fantasy", tone="warm")
        bible.add_character("Tara", {"age": 8, "identity": "locked"})
        bible.add_location("Moonlit Forest", {"time": "night"})
        bible.add_object("Blue Star", {"glow": True})
        return bible

    def test_story_bible_canon(self):
        bible = self.make_bible()
        self.assertEqual(bible.canon_version, 1)
        self.assertEqual(bible.bump_canon(), 2)
        self.assertEqual(CanonGuard(bible).validate({
            "characters": ["Tara"],
            "locations": ["Moonlit Forest"],
            "objects": ["Blue Star"],
        }), [])

    def test_unknown_canon_is_detected(self):
        issues = CanonGuard(self.make_bible()).validate({
            "characters": ["Unknown"],
            "locations": ["Moonlit Forest"],
        })
        self.assertIn("unknown_character:Unknown", issues)

    def test_continuity_state(self):
        tracker = StoryContinuityTracker()
        tracker.apply_scene(1, {
            "characters": {"Tara": {"emotion": "curious"}},
            "objects": {"Blue Star": {"held": True}},
        })
        self.assertEqual(tracker.get_character("Tara")["emotion"], "curious")
        self.assertTrue(tracker.get_object("Blue Star")["held"])

    def test_scene_intent_validation(self):
        intent = SceneIntent("s1", "Tara discovers the star",
                             emotional_goal="wonder",
                             required_characters=["Tara"])
        self.assertEqual(validate_scene_intent(intent), [])
        self.assertEqual(intent.to_dict()["emotional_goal"], "wonder")

    def test_quality_gate(self):
        intent = SceneIntent("s1", "Discovery")
        review = CreativeQualityReviewer().review(intent)
        self.assertTrue(review.passed)
        bad = SceneIntent("", "")
        review2 = CreativeQualityReviewer().review(
            bad, canon_issues=["unknown_character:X"]
        )
        self.assertFalse(review2.passed)
        self.assertGreaterEqual(len(review2.findings), 2)

if __name__ == "__main__":
    unittest.main(verbosity=2)
