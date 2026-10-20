import unittest
from app.core.pipeline import PipelineContext, build_pipeline
from app.engines.production_pipeline import lock_scenes, lock_shots, create_production_manifest

class MasterBatch2Tests(unittest.TestCase):
    def test_pipeline_context(self):
        ctx=PipelineContext("p1")
        cp=ctx.checkpoint("created")
        self.assertEqual(cp["name"],"created")
        self.assertEqual(len(ctx.checkpoints),1)

    def test_scene_lock(self):
        scenes=[{"scene_number":1,"title":"Setup","status":"PLANNED"}]
        locked=lock_scenes(scenes)
        self.assertTrue(locked[0]["continuity_locked"])
        self.assertEqual(locked[0]["status"],"LOCKED")

    def test_shot_lock(self):
        shots=[{"shot_id":"shot_0001","production_status":"PLANNED"}]
        locked=lock_shots(shots)
        self.assertTrue(locked[0]["continuity_locked"])
        self.assertEqual(locked[0]["production_status"],"LOCKED")

    def test_manifest(self):
        manifest=create_production_manifest(
            "p1",
            {"title":"Test Story"},
            [{"scene_number":1,"title":"Setup"}],
            [{"shot_id":"shot_0001"}],
        )
        self.assertEqual(manifest["status"],"READY_FOR_PRODUCTION")
        self.assertEqual(len(manifest["scenes"]),1)
        self.assertEqual(len(manifest["shots"]),1)
        self.assertTrue(manifest["scenes"][0]["continuity_locked"])

    def test_build_pipeline(self):
        ctx=build_pipeline("p1",{"title":"Test"},[],[])
        self.assertEqual(ctx.status,"PLANNED")
        self.assertEqual(ctx.checkpoints[0]["name"],"pipeline_planned")

if __name__=="__main__":
    unittest.main()
