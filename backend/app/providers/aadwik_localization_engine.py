SCHEMA = "aadwik-localization-1.0"

SUPPORTED_LANGUAGES = {
    "en": "English", "te": "Telugu", "hi": "Hindi", "ta": "Tamil",
    "kn": "Kannada", "ml": "Malayalam", "mr": "Marathi", "bn": "Bengali",
    "gu": "Gujarati", "pa": "Punjabi", "ur": "Urdu", "or": "Odia",
    "as": "Assamese"
}

def validate_language(code):
    return code in SUPPORTED_LANGUAGES

def build_localization_job(project_id, source_language, target_languages):
    if not validate_language(source_language):
        raise ValueError("unsupported source language")
    invalid = [x for x in target_languages if not validate_language(x)]
    if invalid:
        raise ValueError("unsupported target language: " + ",".join(invalid))
    return {
        "schema": SCHEMA,
        "project_id": project_id,
        "source_language": source_language,
        "target_languages": target_languages,
        "status": "READY"
    }
