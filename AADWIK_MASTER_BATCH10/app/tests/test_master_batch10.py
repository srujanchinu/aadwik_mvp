import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.integration.master_orchestrator import MasterOrchestrator
from app.core.integration_registry import IntegrationRegistry
from app.core.feature_flags import FeatureFlags

class TestBatch10(unittest.TestCase):
    def test_full_pipeline_order(self):
        result = MasterOrchestrator().run("p1")
        self.assertEqual(result.status, "complete")
        self.assertEqual(result.completed_steps, [
            "story_understanding", "scene_breakdown",
            "character_world_lock", "shot_planning", "generation",
            "alignment_verification", "repair_not_required",
            "final_assembly"
        ])

    def test_repair_branch(self):
        result = MasterOrchestrator().run(
            "p2", context={"repair_required": True}
        )
        self.assertIn("repair", result.completed_steps)

    def test_blocked_pipeline(self):
        result = MasterOrchestrator().run(
            "p3", context={"blocked_at": "generation"}
        )
        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.blocked_steps, ["generation"])

    def test_registry(self):
        reg = IntegrationRegistry()
        reg.register("story_engine", "engine", capabilities=["story"])
        reg.register("local_video_provider", "provider",
                     capabilities=["video"])
        self.assertTrue(reg.ready("story_engine"))
        self.assertEqual(len(reg.by_category("provider")), 1)

    def test_feature_flags(self):
        flags = FeatureFlags({"master_orchestration": True})
        self.assertTrue(flags.enabled("master_orchestration"))
        flags.set("experimental", True)
        self.assertTrue(flags.enabled("experimental"))
        self.assertFalse(flags.enabled("missing"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
