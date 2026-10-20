import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.production.alignment_verifier import AlignmentVerifier
from app.production.repair_planner import RepairPlanner
from app.production.generation_manifest import GenerationManifest
from app.production.verification_pipeline import VerificationPipeline

class TestBatch12(unittest.TestCase):
    def setUp(self):
        self.expected = {
            "characters": ["Tara"],
            "location": "Moonlit Forest",
            "objects": ["Blue Star"],
            "emotion": "wonder",
            "camera": "medium_close",
        }

    def test_alignment_pass(self):
        report = AlignmentVerifier().verify(self.expected, self.expected)
        self.assertTrue(report.passed)
        self.assertEqual(report.score, 1.0)

    def test_alignment_failure(self):
        actual = dict(self.expected)
        actual["emotion"] = "fear"
        report = AlignmentVerifier().verify(self.expected, actual)
        self.assertFalse(report.passed)
        self.assertEqual(report.score, 0.8)
        self.assertEqual(report.findings[0].category, "emotion")

    def test_repair_plan(self):
        report = AlignmentVerifier().verify(
            self.expected, {**self.expected, "camera": "wide"}
        )
        plan = RepairPlanner().plan(report)
        self.assertTrue(plan.required)
        self.assertEqual(plan.actions[0].target, "camera")

    def test_generation_manifest(self):
        manifest = GenerationManifest()
        manifest.record("shot1", "local_blender", "failed")
        manifest.record("shot1", "local_blender", "success", "shot1.mp4")
        self.assertEqual(len(manifest.for_shot("shot1")), 2)
        self.assertEqual(manifest.latest("shot1").status, "success")

    def test_verification_pipeline(self):
        pipeline = VerificationPipeline(
            AlignmentVerifier(), RepairPlanner()
        )
        good = pipeline.evaluate(self.expected, self.expected)
        self.assertEqual(good.status, "approved")
        bad = pipeline.evaluate(
            self.expected, {**self.expected, "characters": ["Unknown"]}
        )
        self.assertEqual(bad.status, "repair_required")
        self.assertTrue(bad.repair_required)

if __name__ == "__main__":
    unittest.main(verbosity=2)
