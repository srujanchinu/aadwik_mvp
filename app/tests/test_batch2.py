import unittest
from app.engines.production_pipeline import build_production_plan
from app.core.manifest import ProductionManifest
from app.core.aadwik_state import ProductionState

class Batch2Tests(unittest.TestCase):
 def test_plan(self):
  p=build_production_plan("A girl finds a glowing star.","p1",scene_count=4,shots_per_scene=3)
  self.assertEqual(len(p["scenes"]),4); self.assertEqual(len(p["shots"]),12)
  self.assertEqual(p["job"].state.state,ProductionState.SHOTS_LOCKED)
  self.assertEqual(len(p["job"].checkpoints),3)
 def test_locks(self):
  p=build_production_plan("test",scene_count=2,shots_per_scene=1)
  self.assertTrue(all(x["continuity_locked"] for x in p["scenes"]))
  self.assertTrue(all(x["continuity_locked"] for x in p["shots"]))
 def test_manifest(self):
  m=ProductionManifest("p1",story={"title":"Test"},scenes=[{"scene_number":1}],shots=[{"shot_id":"shot_1"}])
  d=m.to_dict(); self.assertEqual(d["project_id"],"p1"); self.assertEqual(len(d["shots"]),1)
if __name__=="__main__": unittest.main()
