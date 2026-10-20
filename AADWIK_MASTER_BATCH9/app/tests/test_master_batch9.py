import unittest
from app.providers.provider_contract import ProviderResult,VideoProviderContract
from app.recovery.recovery_engine import RecoveryManager
from app.health.integration_health import run_health_checks

class MasterBatch9Tests(unittest.TestCase):
 def test_provider_result(self):
  r=ProviderResult(True,"movie.mp4","local")
  self.assertTrue(r.success); self.assertEqual(r.provider,"local")
 def test_contract_is_abstract(self):
  self.assertTrue(getattr(VideoProviderContract,"__abstractmethods__"))
 def test_recovery(self):
  m=RecoveryManager(); m.save("rendered",{"frames":10}); m.record_failure("encode","test")
  self.assertTrue(m.can_resume()); self.assertEqual(m.latest().name,"rendered"); self.assertEqual(len(m.failures),1)
 def test_health_pass(self):
  r=run_health_checks([{"name":"story"},{"name":"renderer"}])
  self.assertTrue(r["passed"]); self.assertEqual(r["failed"],[])
 def test_health_fail(self):
  r=run_health_checks([{"name":"renderer"},{"name":"ffmpeg","available":False}])
  self.assertFalse(r["passed"]); self.assertEqual(r["failed"],["ffmpeg"])

if __name__=="__main__": unittest.main()
