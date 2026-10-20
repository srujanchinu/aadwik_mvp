import unittest

from app.integration.e2e_pipeline import EndToEndPipeline, STAGES
from app.integration.stage_contract import validate_contract_chain
from app.integration.pipeline_resume import calculate_resume_point
from app.integration.publish_readiness import evaluate_publish_readiness


class TestMasterBatch20(unittest.TestCase):
    def test_full_end_to_end_flow(self):
        result = EndToEndPipeline().run(
            "job-20-001",
            "A curious girl discovers a glowing blue star in a moonlit forest.",
        )
        self.assertEqual(result.status, "complete")
        self.assertEqual(result.completed_stages, STAGES)
        self.assertTrue(result.artifact["publish_ready"])

    def test_failure_stops_at_failed_stage(self):
        result = EndToEndPipeline().run(
            "job-20-002", "A story", fail_at="generation"
        )
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.stages[4].status, "failed")
        self.assertEqual(len(result.stages), 5)

    def test_contract_chain_is_valid(self):
        report = validate_contract_chain()
        self.assertTrue(report["valid"], report["errors"])

    def test_resume_point(self):
        point = calculate_resume_point(
            "job-20-003",
            STAGES,
            ["story_understanding", "scene_breakdown", "character_world_lock"],
        )
        self.assertTrue(point.resumable)
        self.assertEqual(point.last_passed_stage, "character_world_lock")
        self.assertEqual(point.next_stage, "shot_planning")

    def test_publish_readiness_requires_all_gates(self):
        ready = evaluate_publish_readiness(True, True, True, True)
        self.assertTrue(ready.ready)

        blocked = evaluate_publish_readiness(True, True, False, True)
        self.assertFalse(blocked.ready)
        self.assertIn("approval_required", blocked.reasons)


if __name__ == "__main__":
    unittest.main(verbosity=2)
