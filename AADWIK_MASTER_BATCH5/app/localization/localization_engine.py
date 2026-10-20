LANGUAGE_PACK = [
    "English","Telugu","Hindi","Tamil","Kannada","Malayalam","Marathi",
    "Bengali","Gujarati","Punjabi","Urdu","Odia","Assamese"
]

def supported_languages():
    return list(LANGUAGE_PACK)

def build_localization_plan(title, source_language="English", targets=None):
    targets = list(targets or LANGUAGE_PACK)
    targets = [x for x in targets if x in LANGUAGE_PACK]
    return {
        "title": title,
        "source_language": source_language,
        "targets": targets,
        "preserve_story_intent": True,
        "preserve_character_voice": True,
        "preserve_emotional_meaning": True,
    }

def validate_localized_item(item):
    required=("language","title","text")
    missing=[x for x in required if not item.get(x)]
    return {"passed":not missing,"missing":missing}
