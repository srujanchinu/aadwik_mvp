from aadwik_localization_engine import build_localization_job
from aadwik_translation_engine import translate_story_package
from aadwik_dialogue_localization import localize_dialogue
from aadwik_subtitle_engine import build_subtitles
from aadwik_localized_audio import build_localized_audio

def build_localized_movie(source_package, target_language, voice_map):
    job = build_localization_job(
        source_package["project_id"],
        source_package["source_language"],
        [target_language]
    )
    story = translate_story_package(
        source_package["story"],
        source_package["source_language"],
        target_language
    )
    dialogue = localize_dialogue(source_package["dialogue"], target_language)
    subtitles = build_subtitles(dialogue, target_language)
    audio = build_localized_audio(dialogue, target_language, voice_map)

    return {
        "schema": "aadwik-localized-movie-1.0",
        "localization_job": job,
        "story": story,
        "dialogue": dialogue,
        "subtitles": subtitles,
        "audio": audio,
        "video_identity_locked": True,
        "timing_locked": True,
        "ready_for_localized_render": True
    }
