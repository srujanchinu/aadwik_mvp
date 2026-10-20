def build_subtitles(dialogue_lines, target_language):
    subtitles = []
    for i, line in enumerate(dialogue_lines, 1):
        subtitles.append({
            "index": i,
            "start": line["start"],
            "duration": line["duration"],
            "text": line["text"],
            "language": target_language
        })
    return {
        "schema": "aadwik-subtitle-1.0",
        "language": target_language,
        "subtitles": subtitles,
        "timing_locked": True
    }
