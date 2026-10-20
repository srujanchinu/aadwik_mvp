import unittest
from app.audio.audio_engine import AudioClip, AudioTimeline, plan_audio, validate_audio
from app.editing.edit_engine import VideoClip, EditTimeline, build_edit_timeline, build_assembly_manifest
from app.quality.production_quality import check_video_spec, run_production_quality

class MasterBatch4Tests(unittest.TestCase):
    def test_audio_timeline(self):
        t=AudioTimeline()
        t.add(AudioClip("d1","dialogue",0,2,"voice.wav"))
        t.add(AudioClip("m1","music",2,3,"music.wav"))
        self.assertEqual(t.duration,5)

    def test_audio_planning(self):
        t=plan_audio(
            dialogue=[{"duration":2}],
            music=[{"start":2,"duration":3}],
        )
        self.assertEqual(len(t.clips),2)
        self.assertTrue(validate_audio(t,5))

    def test_edit_timeline(self):
        t=build_edit_timeline([
            {"shot_id":"s1","duration":2},
            {"shot_id":"s2","duration":3},
        ],fps=24)
        self.assertEqual(len(t.clips),2)
        self.assertEqual(t.duration,5)

    def test_assembly_manifest(self):
        t=EditTimeline()
        t.add(VideoClip("s1","a.mp4",0,2))
        m=build_assembly_manifest("movie.mp4",plan_audio(),[])
        self.assertTrue(m["assembly_ready"])
        self.assertEqual(m["audio_duration"],0)

    def test_quality_pass(self):
        t=build_edit_timeline([{"shot_id":"s1","duration":2}])
        r=run_production_quality(
            {"path":"movie.mp4","width":640,"height":360,"fps":8,"duration":2},
            t
        )
        self.assertTrue(r["passed"])
        self.assertEqual(r["score"],100)

    def test_quality_reject(self):
        r=check_video_spec({"path":"x.mp4","width":0,"height":360,"fps":8,"duration":2})
        self.assertFalse(r.passed)

if __name__=="__main__":
    unittest.main()
