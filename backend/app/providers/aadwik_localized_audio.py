def build_localized_audio(dialogue_lines, target_language, voice_map):
    tracks = []
    for line in dialogue_lines:
        character = line["character"]
        if character not in voice_map:
            raise ValueError("missing localized voice for " + character)
        tracks.append({
            "character": character,
            "voice_id": voice_map[character],
            "language": target_language,
            "start": line["start"],
            "duration": line["duration"],
            "emotion": line.get("emotion", "neutral")
        })
    return {
        "schema": "aadwik-localized-audio-1.0",
        "language": target_language,
        "tracks": tracks,
        "timing_locked": True
    }
