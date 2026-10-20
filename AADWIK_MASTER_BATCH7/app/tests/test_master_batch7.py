import unittest
from app.publishing.publishing_engine import PublishingEngine
from app.social.social_command_center import SocialCommandCenter
from app.scheduling.scheduler import Scheduler,validate_iso_datetime

class MasterBatch7Tests(unittest.TestCase):
 def test_publication_lifecycle(self):
  e=PublishingEngine(); p=e.create("p1","YouTube","movie.mp4","Test")
  e.schedule(p,"2026-09-14T10:00:00+05:30"); self.assertEqual(p.status,"SCHEDULED")
  e.approve(p); e.mark_published(p); self.assertEqual(p.status,"PUBLISHED")
 def test_publish_requires_approval(self):
  e=PublishingEngine(); p=e.create("p1","YouTube","movie.mp4")
  with self.assertRaises(ValueError): e.mark_published(p)
 def test_social_connect(self):
  s=SocialCommandCenter(); a=s.connect("YouTube","Aadwik",["publish","analytics"])
  c=s.capabilities(a.account_id); self.assertTrue(c["connected"]); self.assertIn("publish",c["permissions"])
  s.disconnect(a.account_id); self.assertFalse(s.capabilities(a.account_id)["connected"])
 def test_scheduler(self):
  s=Scheduler(); x=s.add("pub1","2026-09-14T10:00:00+05:30")
  self.assertEqual(x.status,"SCHEDULED"); s.cancel(x); self.assertEqual(x.status,"CANCELLED")
 def test_datetime_validation(self):
  self.assertTrue(validate_iso_datetime("2026-09-14T10:00:00+05:30"))
  with self.assertRaises(ValueError): validate_iso_datetime("not-a-date")

if __name__=="__main__": unittest.main()
