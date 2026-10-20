def translate_story_package(story, source_language, target_language):
    if not story.get("title") or not story.get("scenes"):
        raise ValueError("story title and scenes are required")
    return {
        "source_language": source_language,
        "target_language": target_language,
        "title": story["title"],
        "scenes": story["scenes"],
        "translation_status": "READY_FOR_PROVIDER"
    }
