def localize_dialogue(dialogue_lines, target_language):
    localized = []
    for line in dialogue_lines:
        if not line.get("character") or not line.get("text"):
            raise ValueError("dialogue line missing character or text")
        localized.append({
            **line,
            "language": target_language,
            "timing_locked": True,
            "emotion_locked": True
        })
    return localized
