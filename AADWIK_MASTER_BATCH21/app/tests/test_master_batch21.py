import unittest

from app.integration.backend_bridge import BackendBridge
from app.integration.job_mapping import map_movie_job
from app.integration.integration_gate import evaluate_integration_gate
from app.integration.feature_gate import IntegrationFeatureGate


class TestMasterBatch21(unittest.TestCase):
    def test_bridge_defaults_to_safe_disabled_mode(self):
        bridge = BackendBridge()
        job = bridge.prepare_job("movie-21-001", "A story")
        result = bridge.submit(job)
        self.assertFalse(result.accepted)
        self.assertEqual(result.message, "backend bridge disabled")

    def test_enabled_bridge_accepts_job(self):
        bridge = BackendBridge(enabled=True)
        job = bridge.prepare_job("movie-21-002", "A story", source="master_pipeline")
        result = bridge.submit(job)
        self.assertTrue(result.accepted)
        self.assertEqual(result.payload["source"], "master_pipeline")

    def test_job_mapping(self):
        mapping = map_movie_job(
            "movie-21-003", "pipeline-21-003",
            "A glowing star story", style="cinematic"
        )
        payload = mapping.to_backend_payload()
        self.assertEqual(payload["movie_id"], "movie-21-003")
        self.assertEqual(payload["pipeline_job_id"], "pipeline-21-003")
        self.assertEqual(payload["style"], "cinematic")

    def test_integration_gate_requires_all_conditions(self):
        blocked = evaluate_integration_gate(True, True, False, True)
        self.assertFalse(blocked.ready)
        self.assertIn("bridge_disabled", blocked.reasons)

        ready = evaluate_integration_gate(True, True, True, True)
        self.assertTrue(ready.ready)

    def test_feature_gate_is_explicit(self):
        gate = IntegrationFeatureGate()
        self.assertFalse(gate.enabled)
        gate.enable()
        self.assertTrue(gate.enabled)
        gate.disable()
        self.assertFalse(gate.enabled)


if __name__ == "__main__":
    unittest.main(verbosity=2)
