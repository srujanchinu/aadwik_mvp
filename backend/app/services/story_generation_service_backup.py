
import json
import os
import re

from google import genai


DEFAULT_MODEL = "gemini-3.8-flash"


class StoryGenerationError(RuntimeError):
    """Raised when Aadwik cannot create a valid screenplay."""


def _get_client():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        raise StoryGenerationError(
            "GEMINI_API_KEY is missing. Configure it before generating a story."
        )

    if api_key == "PASTE_YOUR_REAL_GEMINI_API_KEY_HERE":
        raise StoryGenerationError(
            "GEMINI_API_KEY still contains placeholder text."
        )

    return genai.Client(api_key=api_key)


def _extract_json(response_text: str) -> dict:
    text = (response_text or "").strip()

    # Remove Markdown fences if the model includes them.
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")

        if start < 0 or end <= start:
            raise StoryGenerationError(
                "Gemini returned no valid JSON screenplay."
            )

        try:
            data = json.loads(text[start:end + 1])
        except json.JSONDecodeError as exc:
            raise StoryGenerationError(
                "Gemini returned malformed screenplay JSON."
            ) from exc

    if not isinstance(data, dict):
        raise StoryGenerationError(
            "The screenplay response must be a JSON object."
        )

    return data


def generate_screenplay(
    prompt: str,
    language: str = "English",
    duration_minutes: int = 5,
    genre: str = "Fantasy",
    age_group: str = "All Ages",
    character_type: str = "Mixed",
) -> dict:
    """Generate a complete screenplay with ordered scenes and dialogue."""

    prompt = (prompt or "").strip()
    language = (language or "English").strip()
    genre = (genre or "Fantasy").strip()
    age_group = (age_group or "All Ages").strip()
    character_type = (character_type or "Mixed").strip()

    if len(prompt) < 5:
        raise StoryGenerationError(
            "Please provide a story idea of at least 5 characters."
        )

    if not 1 <= duration_minutes <= 30:
        raise StoryGenerationError(
            "Movie duration must be between 1 and 30 minutes."
        )

    # Approximate narration length at 125-145 words per minute.
    target_words = duration_minutes * 135
    minimum_words = int(target_words * 0.90)
    maximum_words = int(target_words * 1.15)

    model = os.getenv("GEMINI_TEXT_MODEL", DEFAULT_MODEL).strip()
    if not model:
        model = DEFAULT_MODEL

    instructions = f"""
You are Aadwik's professional screenplay writer. Create an original, emotionally engaging, natural-sounding, complete screenplay from the user's story idea.

TARGET LENGTH:
- Target approximately {target_words} spoken words.
- Minimum acceptable length: {minimum_words} words.
- Maximum acceptable length: {maximum_words} words.
- Count all narration and spoken dialogue toward the target.
- Do not return a synopsis or compressed summary instead of a full screenplay.

STORY QUALITY:
- Establish the characters, setting, goal, and central problem clearly.
- Develop the story through connected events, meaningful character choices, obstacles, and consequences.
- Include natural dialogue that sounds like real characters speaking.
- Give every scene a clear purpose and a smooth transition to the next scene.
- Build emotional engagement and resolve the main conflict convincingly.
- Include a complete ending, not an abrupt stop.
- Respect the selected language, genre, age group, and character type.
- For children's stories, use age-appropriate language and a positive, understandable takeaway.
- Ensure narration and dialogue are not repetitive filler.

SCENE REQUIREMENTS:
- Create enough scenes to tell the full story at the requested duration.
- Each scene must include scene_number, title, setting, visual_description, action, dialogue, narration, emotion, camera_direction, sound_effects, and music_mood.
- Dialogue must be a list of objects containing character and line.
- Narration must advance the story and connect events naturally.
- Visual descriptions must show concrete actions that can be animated.

Return valid JSON only, using these fields:
title, language, genre, target_duration_minutes, synopsis, characters, scenes, ending, moral_or_takeaway.

Before returning the JSON, check that the story is complete and that the combined narration and dialogue meet the requested word-count range. If they are too short, expand the actual story with meaningful events and dialogue.
REQUIREMENTS
- Output language: {language}
- Genre: {genre}
- Audience: {age_group}
- Character type: {character_type}
- Target duration: {duration_minutes} minutes
- Approximate spoken-word target: {target_words} words
- Use natural, speakable language suitable for narration.
- Maintain consistent character names, personalities, and motivations.
- Include a clear beginning, escalating events, meaningful turning
  points, a climax, and a satisfying ending.
- Every scene must advance the plot or develop a character.
- Write actual dialogue where appropriate, not generic placeholders.
- Make visual action concrete enough for an animation team to stage.
- Respect the audience's age and cultural context.
- Do not claim the screenplay is longer than it actually is.
- Do not add explanations outside the requested JSON.

Return one valid JSON object in this exact structure:
{{
  "title": "Story title",
  "language": "{language}",
  "genre": "{genre}",
  "target_duration_minutes": {duration_minutes},
  "synopsis": "Short synopsis",
  "characters": [
    {{
      "name": "Character name",
      "description": "Appearance and personality",
      "role": "Story role"
    }}
  ],
  "scenes": [
    {{
      "scene_number": 1,
      "title": "Scene title",
      "setting": "Location and time",
      "visual_description": "Specific visible action and environment",
      "action": "What happens in this scene",
      "dialogue": [
        {{
          "character": "Character name or Narrator",
          "line": "Spoken dialogue in the requested language"
        }}
      ],
      "narration": "Narration for this scene in the requested language",
      "emotion": "Dominant emotional tone",
      "camera_direction": "Suggested camera framing and movement",
      "sound_effects": ["Relevant sound effects"],
      "music_mood": "Suggested music mood"
    }}
  ],
  "ending": "How the story concludes",
  "moral_or_takeaway": "Optional lesson, or empty string if unsuitable"
}}

Make the screenplay long enough for the requested duration. Use as many
scenes as the story needs. Never substitute placeholder scenes or
repeated generic descriptions for real story development.
"""

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=model,
            contents=(
                instructions
                + "\n\nSTORY IDEA:\n"
                + prompt
            ),
            config={
                "response_mime_type": "application/json",
                "temperature": 0.8,
            },
        )
    except Exception as exc:
        raise StoryGenerationError(
            f"Gemini screenplay generation failed: {type(exc).__name__}: {exc}"
        ) from exc

    screenplay = _extract_json(
        getattr(response, "text", "") or ""
    )

    title = screenplay.get("title")
    scenes = screenplay.get("scenes")

    if not isinstance(title, str) or not title.strip():
        raise StoryGenerationError(
            "Screenplay is missing its title."
        )

    if not isinstance(scenes, list) or not scenes:
        raise StoryGenerationError(
            "Screenplay contains no scenes."
        )

    for index, scene in enumerate(scenes, start=1):
        if not isinstance(scene, dict):
            raise StoryGenerationError(
                f"Scene {index} is not a valid object."
            )

        scene["scene_number"] = index

        if not str(scene.get("title", "")).strip():
            raise StoryGenerationError(
                f"Scene {index} is missing its title."
            )

        if not str(scene.get("action", "")).strip():
            raise StoryGenerationError(
                f"Scene {index} is missing its action."
            )

        dialogue = scene.get("dialogue", [])
        if not isinstance(dialogue, list):
            raise StoryGenerationError(
                f"Scene {index} dialogue must be a list."
            )

    screenplay["title"] = title.strip()
    screenplay["language"] = language
    screenplay["genre"] = genre
    screenplay["target_duration_minutes"] = duration_minutes

    screenplay["word_count"] = len(
        " ".join(
            str(scene.get("narration", ""))
            + " "
            + " ".join(
                str(line.get("line", ""))
                for line in scene.get("dialogue", [])
            )
            for scene in screenplay["scenes"]
        ).split()
    )

    if screenplay["word_count"] < minimum_words:
        retry_instructions = (
            instructions
            + "\n\nIMPORTANT RETRY: Your previous screenplay was too short. "
            + f"It contained {screenplay['word_count']} words, but at least "
            + f"{minimum_words} spoken words are required. "
            + "Write a fuller, complete screenplay with additional meaningful "
            + "events, natural dialogue, detailed narration, and a satisfying "
            + "ending. Meet the required word count. Return valid JSON only."
            + "\n\nPREVIOUS SCREENPLAY:\n"
            + json.dumps(screenplay, ensure_ascii=False)
        )

        try:
            retry_response = client.models.generate_content(
                model=model,
                contents=retry_instructions,
                config={
                    "response_mime_type": "application/json",
                    "temperature": 0.8,
                },
            )
            screenplay = _extract_json(
                getattr(retry_response, "text", "") or ""
            )
        except Exception as exc:
            raise StoryGenerationError(
                f"Screenplay expansion retry failed: {type(exc).__name__}: {exc}"
            ) from exc

        # Preserve and validate the required screenplay fields.
        if not isinstance(screenplay.get("scenes"), list) or not screenplay["scenes"]:
            raise StoryGenerationError(
                "Expanded screenplay contains no scenes."
            )

        screenplay["title"] = str(screenplay.get("title", "")).strip()
        screenplay["language"] = language
        screenplay["genre"] = genre
        screenplay["target_duration_minutes"] = duration_minutes

        screenplay["word_count"] = len(
            " ".join(
                str(scene.get("narration", ""))
                + " "
                + " ".join(
                    str(line.get("line", ""))
                    for line in scene.get("dialogue", [])
                    if isinstance(line, dict)
                )
                for scene in screenplay["scenes"]
                if isinstance(scene, dict)
            ).split()
        )

        if screenplay["word_count"] < minimum_words:
            raise StoryGenerationError(
                f"Expanded screenplay still too short: "
                f"{screenplay['word_count']} words; "
                f"minimum required: {minimum_words}."
            )

    return screenplay
