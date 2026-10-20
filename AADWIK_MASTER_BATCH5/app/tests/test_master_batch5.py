import unittest
from app.localization.localization_engine import supported_languages, build_localization_plan, validate_localized_item
from app.kids.little_wonders import get_age_track, build_kids_content_plan
from app.heritage.mythology import build_heritage_content_plan, validate_heritage_plan

class MasterBatch5Tests(unittest.TestCase):
    def test_language_pack(self):
        langs=supported_languages()
        self.assertEqual(len(langs),13)
        self.assertIn("Telugu",langs)
        self.assertIn("Assamese",langs)

    def test_localization_plan(self):
        p=build_localization_plan("Story",targets=["Telugu","Hindi","English"])
        self.assertEqual(len(p["targets"]),3)
        self.assertTrue(p["preserve_character_voice"])

    def test_localization_validation(self):
        self.assertTrue(validate_localized_item({"language":"Telugu","title":"T","text":"x"})["passed"])
        self.assertFalse(validate_localized_item({"language":"Telugu"})["passed"])

    def test_little_wonders_tracks(self):
        self.assertEqual(get_age_track(3)["name"],"Little Kids")
        self.assertEqual(get_age_track(6)["name"],"Adventure Kids")
        self.assertEqual(get_age_track(9)["name"],"Big Kids")

    def test_kids_plan(self):
        p=build_kids_content_plan(6,"space adventure")
        self.assertTrue(p["story_first"])
        self.assertEqual(p["learning_style"],"natural_in_story")

    def test_heritage(self):
        p=build_heritage_content_plan("Ramayana","Telugu","Family")
        self.assertTrue(p["respect_cultural_context"])
        self.assertTrue(validate_heritage_plan(p)["passed"])

if __name__=="__main__":
    unittest.main()
