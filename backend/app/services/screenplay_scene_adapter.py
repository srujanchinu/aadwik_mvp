from app.services.story_generation_service import (
    generate_screenplay,
    StoryGenerationError,
)


def generate_movie_scenes(
    prompt: str,
    genre: str,
    duration_minutes: int,
    character_type: str,
    music_mood: str,
    sound_effects_enabled: bool,
    language: str = "English",
    age_group: str = "All Ages",
) -> list[dict]:
    """Convert an AI screenplay into Aadwik's existing scene format."""

    screenplay = generate_screenplay(
        prompt=prompt,
        language=language,
        duration_minutes=duration_minutes,
        genre=genre,
        age_group=age_group,
        character_type=character_type,
    )

    screenplay_scenes = screenplay.get("scenes", [])
    if not screenplay_scenes:
        raise StoryGenerationError("The screenplay contains no scenes.")

    default_music = "Fantasy / Magical" if music_mood == "Auto" else music_mood
    scene_duration = max(1, (duration_minutes * 60) // len(screenplay_scenes))
    movie_scenes = []

    for index, source in enumerate(screenplay_scenes, start=1):
        dialogue_items = source.get("dialogue", [])
        dialogue_text = "\n".join(
            f"{item.get('character', 'Character')}: {item.get('line', '')}"
            for item in dialogue_items
            if isinstance(item, dict) and item.get("line")
        )

        narration = source.get("narration", "")
        dialogue = "\n".join(part for part in [narration, dialogue_text] if part)

        description_parts = [
            source.get("setting", ""),
            source.get("visual_description", ""),
            source.get("action", ""),
        ]
        description = " ".join(
            part.strip() for part in description_parts
            if isinstance(part, str) and part.strip()
        )

        movie_scenes.append({
            "scene_number": index,
            "title": source.get("title") or f"Scene {index}",
            "description": description or prompt,
            "characters": [character_type],
            "dialogue": dialogue or narration or prompt,
            "emotion": source.get("emotion", "Curiosity"),
            "visual_direction": source.get("visual_description", description or prompt),
            "camera_direction": source.get("camera_direction", "Cinematic medium and wide shots."),
            "music_mood": source.get("music_mood") or default_music,
            "sound_effects": (
                source.get("sound_effects", [])
                if sound_effects_enabled else []
            ),
            "estimated_duration_seconds": scene_duration,
            "status": "PLANNED",
            "production_step": "Waiting for production.",
            "progress": 0,
        })

    return movie_scenes
