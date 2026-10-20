import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.production.shot_plan import ShotPlanner
from app.production.asset_requirements import AssetRequirementBuilder
from app.production.execution_contract import ExecutionContractBuilder
from app.production.production_batch import ProductionBatch

class TestBatch13(unittest.TestCase):
    def setUp(self):
        self.scene = {
            "scene_id": "scene_01",
            "purpose": "Tara discovers the glowing star",
            "characters": ["Tara", "Guardian"],
            "location": "Moonlit Forest",
            "objects": ["Blue Star"],
            "emotion": "wonder",
            "action": "Tara reaches toward the star",
        }

    def test_shot_planning(self):
        shots = ShotPlanner().plan(self.scene)
        self.assertEqual(len(shots), 2)
        self.assertEqual(shots[0].camera, "establishing")
        self.assertEqual(shots[1].camera, "medium_close")
        self.assertEqual(shots[1].characters, ["Tara", "Guardian"])

    def test_asset_requirements(self):
        shot = ShotPlanner().plan(self.scene)[0]
        assets = AssetRequirementBuilder().build_for_shot(shot)
        ids = [a.asset_id for a in assets]
        self.assertIn("character:Tara", ids)
        self.assertIn("location:Moonlit Forest", ids)
        self.assertIn("object:Blue Star", ids)

    def test_execution_contract(self):
        shot = ShotPlanner().plan(self.scene)[1]
        assets = AssetRequirementBuilder().build_for_shot(shot)
        contract = ExecutionContractBuilder().build(shot, assets)
        self.assertEqual(contract.status, "planned")
        self.assertEqual(contract.provider, "local_blender")
        contract.mark_generating()
        contract.mark_complete("shot.mp4")
        self.assertEqual(contract.status, "generated")
        self.assertEqual(contract.output_path, "shot.mp4")

    def test_failed_contract(self):
        shot = ShotPlanner().plan(self.scene)[0]
        contract = ExecutionContractBuilder().build(shot, [])
        contract.mark_generating()
        contract.mark_failed()
        self.assertEqual(contract.status, "failed")

    def test_production_batch(self):
        batch = ProductionBatch("project_01")
        shots = ShotPlanner().plan(self.scene)
        for shot in shots:
            assets = AssetRequirementBuilder().build_for_shot(shot)
            batch.add(ExecutionContractBuilder().build(shot, assets))
        self.assertEqual(len(batch.pending()), 2)
        self.assertFalse(batch.complete())
        for contract in batch.contracts:
            contract.mark_complete(f"{contract.shot_id}.mp4")
        self.assertEqual(len(batch.generated()), 2)
        self.assertTrue(batch.complete())

if __name__ == "__main__":
    unittest.main(verbosity=2)
