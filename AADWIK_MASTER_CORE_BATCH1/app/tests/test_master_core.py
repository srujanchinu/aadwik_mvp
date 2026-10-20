import unittest
from app.core.aadwik_state import *
from app.core.project_context import build_story_bible
from app.core.production_job import ProductionJob
from app.core.quality_gate import *
from app.engines.story_engine import *
from app.engines.character_engine import *
from app.engines.shot_engine import *
class MasterCoreTests(unittest.TestCase):
 def test_state(self):
  s=ProductionStateRecord(); s.transition(ProductionState.STORY_LOCKED); s.transition(ProductionState.SCENES_LOCKED); self.assertEqual(s.state,ProductionState.SCENES_LOCKED)
  with self.assertRaises(ValueError): s.transition(ProductionState.PUBLISHED)
 def test_story(self): self.assertEqual(len(breakdown_scenes(understand_story('A girl finds a glowing star.'),5)),5)
 def test_locks(self): self.assertTrue(lock_character({'name':'Tara'}).identity_locked); self.assertTrue(lock_world({'name':'Forest'}).identity_locked)
 def test_bible(self):
  b=build_story_bible('p',{'characters':[{'character_id':'tara','name':'Tara'}],'locations':['forest']}); self.assertIn('tara',b.locked_character_ids()); self.assertIn('forest',b.locked_world_ids())
 def test_shots(self): self.assertEqual(len(plan_shots(breakdown_scenes(understand_story('x'),3),2)),6)
 def test_job(self):
  j=ProductionJob(project_id='p'); j.checkpoint('story'); self.assertIsNotNone(j.latest_checkpoint())
 def test_gate(self): self.assertTrue(run_quality_gates({'title':'x'},[required_field_gate('title','title')]).passed)
if __name__=='__main__': unittest.main()
