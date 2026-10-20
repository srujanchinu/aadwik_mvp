import unittest
from app.analytics.analytics_engine import AnalyticsEngine,MetricSnapshot
from app.insights.insight_engine import generate_insights
from app.experiments.experiment_mode import Experiment

class MasterBatch8Tests(unittest.TestCase):
 def test_metric_calculation(self):
  x=MetricSnapshot("YouTube",views=100,likes=10,comments=5,shares=5)
  self.assertEqual(x.engagement_rate,0.2)
 def test_analytics_summary(self):
  e=AnalyticsEngine(); e.record(MetricSnapshot("YouTube",100,10,2,3)); e.record(MetricSnapshot("YouTube",200,20,4,6))
  s=e.platform_summary("YouTube")
  self.assertEqual(s["views"],300); self.assertEqual(s["count"],2)
 def test_insights(self):
  rows=[MetricSnapshot("YouTube",100),MetricSnapshot("Instagram",250)]
  r=generate_insights(rows)
  self.assertEqual(r["total_views"],350); self.assertTrue(r["recommendations"])
 def test_experiment_requires_variants(self):
  e=Experiment("Test","Does version A outperform B?")
  with self.assertRaises(ValueError): e.start()
 def test_experiment_start(self):
  e=Experiment("Test","Compare thumbnails"); e.add_variant("A",{"thumbnail":"a"}); e.add_variant("B",{"thumbnail":"b"}); e.start()
  self.assertEqual(e.status,"RUNNING"); self.assertEqual(len(e.variants),2)

if __name__=="__main__": unittest.main()
