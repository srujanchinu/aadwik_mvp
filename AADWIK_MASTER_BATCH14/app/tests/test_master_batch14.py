import sys
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.production.asset_lock import AssetLockManager
from app.production.shot_continuity import ShotContinuityValidator
from app.production.prompt_contract import PromptContractBuilder
from app.production.asset_readiness import AssetReadinessGate
from app.production.shot_plan import ShotPlanner
from app.production.asset_requirements import AssetRequirementBuilder

class TestBatch14(unittest.TestCase):
    def setUp(self):
        self.scene = {"scene_id":"s1","purpose":"discovery","characters":["Tara"],
                      "location":"Forest","objects":["Blue Star"],"emotion":"wonder",
                      "action":"reach"}

    def test_asset_lock(self):
        m = AssetLockManager()
        m.lock("character:Tara","character",{"age":8,"hair":"dark"})
        self.assertEqual(m.validate("character:Tara",{"age":8,"hair":"dark"}), [])
        self.assertIn("identity_mismatch:hair",
                      m.validate("character:Tara",{"age":8,"hair":"light"}))

    def test_shot_continuity(self):
        shots = ShotPlanner().plan(self.scene)
        bridge = ShotContinuityValidator().bridge(shots[0].to_dict(), shots[1].to_dict())
        self.assertEqual(bridge.previous_shot,"s1_shot_01")
        self.assertEqual(ShotContinuityValidator().validate(
            shots[1], {"location":"Forest"}, {"location":"Forest"}), [])

    def test_prompt_contract(self):
        shot = ShotPlanner().plan(self.scene)[0]
        c = PromptContractBuilder().build(shot, {"character_identity":"Tara-v2"})
        self.assertIn("SHOT s1_shot_01", c.render())
        self.assertIn("character_identity=Tara-v2", c.render())
        self.assertIn("identity drift", c.render())

    def test_readiness(self):
        shot = ShotPlanner().plan(self.scene)[0]
        reqs = AssetRequirementBuilder().build_for_shot(shot)
        report = AssetReadinessGate().check(reqs, ["character:Tara"])
        self.assertFalse(report.ready)
        self.assertIn("location:Forest", report.missing)

    def test_readiness_complete(self):
        shot = ShotPlanner().plan(self.scene)[0]
        reqs = AssetRequirementBuilder().build_for_shot(shot)
        self.assertTrue(AssetReadinessGate().check(reqs,[a.asset_id for a in reqs]).ready)

if __name__ == "__main__":
    unittest.main(verbosity=2)
