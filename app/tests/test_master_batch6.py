import unittest
from app.planning.production_queue import ProductionQueue,QueueItem
from app.assets.asset_library import AssetLibrary,Asset
from app.cost.cost_protection import CostBudget,estimate_cost
from app.ideas.idea_bank import IdeaBank,Idea

class MasterBatch6Tests(unittest.TestCase):
 def test_queue_priority(self):
  q=ProductionQueue(); low=q.add(QueueItem(project_id="low",priority=10)); high=q.add(QueueItem(project_id="high",priority=90))
  self.assertIs(q.next_item(),high); q.mark_running(high); self.assertEqual(high.status,"RUNNING")
 def test_asset_versions(self):
  lib=AssetLibrary(); a=lib.register_version("Tara","character"); b=lib.register_version("Tara","character")
  self.assertEqual(a.version,1); self.assertEqual(b.version,2); self.assertEqual(len(lib.versions("Tara")),2)
 def test_cost_protection(self):
  b=CostBudget(limit=10); self.assertTrue(b.can_spend(6)); b.spend(6)
  self.assertEqual(b.remaining,4); self.assertFalse(b.can_spend(5))
  with self.assertRaises(ValueError): b.spend(5)
 def test_cost_estimate(self): self.assertEqual(estimate_cost(5,2),10)
 def test_idea_bank(self):
  bank=IdeaBank(); idea=bank.add(Idea("Moon Guardian","A child helps a guardian","fantasy"))
  self.assertEqual(len(bank.search("guardian")),1); bank.promote(idea); self.assertEqual(idea.status,"PLANNED")

if __name__=="__main__": unittest.main()
