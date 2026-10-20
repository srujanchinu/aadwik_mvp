from datetime import datetime, timezone, timedelta
import random
from time import sleep
from uuid import uuid4
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.movie_store import store
from app.services.content_queue_store import content_queue_store
from app.providers.local_video_provider import LocalVideoProvider


router = APIRouter(
    prefix="/movies",
    tags=["movies"],
)
# ============================================================
# AADWIK RANDOM STORY ENGINE
# ============================================================

def generate_random_story(
    niche: str,
):
    niche_lower = niche.lower().strip()

    # --------------------------------------------------------
    # MYTHOLOGY / SPIRITUAL
    # --------------------------------------------------------

    if (
        "myth" in niche_lower
        or "spiritual" in niche_lower
        or "legend" in niche_lower
    ):
        heroes = [
            "a young temple guardian",
            "a curious village child",
            "a brave young traveler",
            "a kind-hearted apprentice",
            "a determined young explorer",
        ]

        locations = [
            "an ancient mountain temple",
            "a forgotten riverside shrine",
            "a hidden valley surrounded by clouds",
            "an old kingdom filled with mysterious ruins",
            "a sacred forest protected by ancient guardians",
        ]

        discoveries = [
            "a forgotten symbol that begins to glow",
            "an ancient bell that rings without anyone touching it",
            "a mysterious path visible only at sunrise",
            "a lost scroll containing an important lesson",
            "a hidden doorway leading to a forgotten chamber",
        ]

        challenges = [
            "must overcome fear and continue the journey",
            "must help strangers before solving the mystery",
            "must choose kindness instead of taking an easy reward",
            "must solve a series of ancient clues",
            "must learn to trust courage and wisdom",
        ]

        lessons = [
            "true strength comes from compassion",
            "courage is strongest when used to help others",
            "wisdom grows when people listen and learn",
            "kindness can change even difficult situations",
            "real victory comes from doing what is right",
        ]

        hero = random.choice(heroes)
        location = random.choice(locations)
        discovery = random.choice(discoveries)
        challenge = random.choice(challenges)
        lesson = random.choice(lessons)

        title = random.choice(
            [
                "The Path of Courage",
                "The Hidden Light",
                "The Guardian's Promise",
                "The Temple of Wisdom",
                "The Forgotten Bell",
                "The Journey of the Sacred Valley",
            ]
        )

        story = (
            f"{hero.capitalize()} begins an unexpected journey to "
            f"{location}. There, the young hero discovers "
            f"{discovery}. To understand its meaning, the hero "
            f"{challenge}. By the end of the adventure, the hero "
            f"discovers that {lesson}."
        )

        return {
            "title": title,
            "story": story,
            "genre": "Mythological",
            "recommended_style": "Cinematic Animation",
            "character_type": "Human",
            "music_mood": "Fantasy / Magical",
            "talking_animals": False,
        }

    # --------------------------------------------------------
    # EDUCATIONAL
    # --------------------------------------------------------

    if (
        "educ" in niche_lower
        or "learning" in niche_lower
        or "science" in niche_lower
    ):
        children = [
            "a curious young inventor",
            "a creative school student",
            "a child who loves asking questions",
            "a young science enthusiast",
            "a clever young builder",
        ]

        topics = [
            "how plants grow",
            "how simple machines work",
            "how recycling helps the environment",
            "how water moves through nature",
            "how light and shadows change",
            "how magnets attract and repel objects",
        ]

        problems = [
            "a problem at home",
            "a challenge in the school garden",
            "a mystery in the classroom",
            "a project that initially goes wrong",
            "a problem affecting the local community",
        ]

        solutions = [
            "careful observation and experimentation",
            "creativity and teamwork",
            "scientific thinking",
            "testing different ideas",
            "learning from mistakes",
        ]

        child = random.choice(children)
        topic = random.choice(topics)
        problem = random.choice(problems)
        solution = random.choice(solutions)

        title = random.choice(
            [
                "The Curious Discovery",
                "The Young Inventor's Challenge",
                "The Amazing Question",
                "A Brilliant Little Experiment",
                "The Mystery of Learning",
            ]
        )

        story = (
            f"{child.capitalize()} becomes fascinated by "
            f"{topic}. When {problem} appears, the young learner "
            f"uses {solution} to discover a solution. Along the "
            f"way, the adventure makes learning about {topic} "
            f"fun, practical, and exciting."
        )

        return {
            "title": title,
            "story": story,
            "genre": "Educational",
            "recommended_style": "3D Animation",
            "character_type": "Human",
            "music_mood": "Educational / Learning",
            "talking_animals": False,
        }

    # --------------------------------------------------------
    # COMEDY
    # --------------------------------------------------------

    if (
        "comedy" in niche_lower
        or "funny" in niche_lower
    ):
        characters = [
            "a mischievous monkey",
            "an overly confident dog",
            "a clumsy young magician",
            "a cheerful little robot",
            "a forgetful inventor",
        ]

        mistakes = [
            "accidentally mixes up everyone's belongings",
            "creates a ridiculous invention that causes chaos",
            "turns an ordinary celebration into a series of surprises",
            "misunderstands an important message",
            "tries to solve a simple problem in the funniest possible way",
        ]

        endings = [
            "everyone discovers that laughing together can solve more than arguments",
            "the character learns that asking for help is sometimes the smartest choice",
            "the unexpected mistakes lead to a wonderful new friendship",
            "the whole community turns the disaster into a celebration",
            "the character discovers that being imperfect can still bring happiness",
        ]

        character = random.choice(characters)
        mistake = random.choice(mistakes)
        ending = random.choice(endings)

        title = random.choice(
            [
                "The Great Mix-Up",
                "Oops! Another Adventure",
                "The Funniest Day Ever",
                "A Very Silly Mission",
                "The Unexpected Laugh",
            ]
        )

        story = (
            f"{character.capitalize()} {mistake}. While trying "
            f"to fix the situation, every solution creates an "
            f"even funnier problem. Eventually, {ending}."
        )

        return {
            "title": title,
            "story": story,
            "genre": "Comedy",
            "recommended_style": "3D Animation",
            "character_type": "Mixed",
            "music_mood": "Happy / Fun",
            "talking_animals": True,
        }

    # --------------------------------------------------------
    # VEHICLES
    # --------------------------------------------------------

    if (
        "vehicle" in niche_lower
        or "car" in niche_lower
        or "train" in niche_lower
        or "bike" in niche_lower
        or "racing" in niche_lower
    ):
        heroes = [
            "a young racing car",
            "a brave little train",
            "an adventurous bicycle",
            "a curious electric car",
            "a determined rescue vehicle",
        ]

        missions = [
            "deliver an important package before sunset",
            "find a safe route through an unfamiliar region",
            "help another vehicle that has become lost",
            "work with a team during an exciting race",
            "solve a problem that blocks an important journey",
        ]

        locations = [
            "a mountain road",
            "a busy futuristic city",
            "a colorful countryside",
            "a desert racing track",
            "a magical transport world",
        ]

        hero = random.choice(heroes)
        mission = random.choice(missions)
        location = random.choice(locations)

        title = random.choice(
            [
                "The Road to Adventure",
                "The Great Journey",
                "The Fastest Friendship",
                "Mission on Wheels",
                "The Race Beyond the Horizon",
            ]
        )

        story = (
            f"{hero.capitalize()} travels through {location} "
            f"with one important goal: to {mission}. Along the "
            f"way, unexpected obstacles require courage, "
            f"teamwork, and clever thinking. The journey proves "
            f"that success is more meaningful when friends help "
            f"one another."
        )

        return {
            "title": title,
            "story": story,
            "genre": "Adventure",
            "recommended_style": "3D Animation",
            "character_type": "Vehicles",
            "music_mood": "Adventure / Energetic",
            "talking_animals": False,
        }

    # --------------------------------------------------------
    # DEFAULT FANTASY / ADVENTURE
    # --------------------------------------------------------

    heroes = [
        "a young explorer",
        "a brave young girl",
        "a curious young boy",
        "two adventurous friends",
        "a young guardian",
        "a clever child with a mysterious map",
    ]

    worlds = [
        "a floating island above the clouds",
        "a hidden underwater kingdom",
        "a glowing crystal cave",
        "a mysterious forest that changes every night",
        "a forgotten city hidden inside the mountains",
        "a magical village where unusual things happen",
    ]

    discoveries = [
        "a mysterious map",
        "a lost magical creature",
        "an ancient glowing key",
        "a secret doorway",
        "a strange object with unknown powers",
        "a message from someone who needs help",
    ]

    conflicts = [
        "find the missing path before the world changes forever",
        "help a frightened creature return home",
        "solve a mystery before sunset",
        "protect a magical place from danger",
        "work with new friends to overcome an unexpected obstacle",
        "discover why the world around them is slowly changing",
    ]

    endings = [
        "kindness and courage bring everyone together",
        "the hero discovers that friendship is more powerful than magic",
        "the adventure ends with a surprising discovery that opens the door to another journey",
        "the characters return home with a deeper understanding of one another",
        "the mysterious world becomes safe again because everyone chooses to work together",
    ]

    hero = random.choice(heroes)
    world = random.choice(worlds)
    discovery = random.choice(discoveries)
    conflict = random.choice(conflicts)
    ending = random.choice(endings)

    title = random.choice(
        [
            "Beyond the Hidden World",
            "The Secret Adventure",
            "The Door Beyond Tomorrow",
            "The Lost World Mystery",
            "The Journey of the Glowing Key",
            "The Adventure Nobody Expected",
            "The World Behind the Clouds",
            "The Mystery of the Forgotten City",
        ]
    )

    story = (
        f"{hero.capitalize()} discovers {world} after finding "
        f"{discovery}. What begins as a simple adventure quickly "
        f"becomes a mission to {conflict}. Along the journey, "
        f"new friendships and unexpected discoveries change "
        f"everything. In the end, {ending}."
    )

    return {
        "title": title,
        "story": story,
        "genre": "Fantasy",
        "recommended_style": "3D Animation",
        "character_type": "Humans + Animals",
        "music_mood": "Fantasy / Magical",
        "talking_animals": True,
    }

# ============================================================
# AUTO STORY MODELS
# ============================================================

class AutoStoryRequest(BaseModel):
    niche: str = "Auto"
    language: str = "Auto"
    age_group: str = "Auto"


class AutoStoryResponse(BaseModel):
    title: str
    story: str
    genre: str
    age_group: str
    recommended_style: str
    character_type: str
    music_mood: str
    talking_animals: bool


# ============================================================
# MOVIE REQUEST MODEL
# ============================================================

class CreateMovieRequest(BaseModel):
    # Story
    prompt: str = Field(
        min_length=5,
        max_length=20000,
    )

    # Basic settings
    style: str
    language: str
    duration_minutes: int = Field(
        ge=1,
        le=30,
    )

    # Content settings
    genre: str = "Fantasy"
    age_group: str = "All Ages"
    character_type: str = "Mixed"

    # Music and audio
    music_mood: str = "Auto"
    scene_based_music: bool = True
    sound_effects: bool = True

    # Platform
    platform: str = "YouTube Video"
    aspect_ratio: str = "16:9"

    # Characters
    talking_animals: bool = False
    lip_sync: bool = True

    # Accessibility
    subtitles: bool = True

    # Thumbnail
    auto_generate_thumbnail: bool = True
    thumbnail_style: str = "Cinematic"
    thumbnail_title: str = ""
    thumbnail_expression: str = "Excited"
    include_main_character: bool = True


# ============================================================
# APPROVAL REQUEST MODEL
# ============================================================


class ApprovalRequest(BaseModel):
    action: str
    reason: str | None = None

# ============================================================
# SCHEDULE REQUEST MODEL
# ============================================================

class ScheduleMovieRequest(BaseModel):
    scheduled_at: str
    platform: str = "YouTube"
    timezone: str = "Asia/Kolkata"


# ============================================================
# SCENE RESPONSE MODEL
# ============================================================

class SceneResponse(BaseModel):
    scene_number: int
    title: str
    description: str
    characters: list[str]
    dialogue: str
    emotion: str
    visual_direction: str
    camera_direction: str
    music_mood: str
    sound_effects: list[str]
    estimated_duration_seconds: int

    # Production status
    status: str
    production_step: str
    progress: int


# ============================================================
# MOVIE RESPONSE MODEL
# ============================================================

class MovieResponse(BaseModel):
    # Core movie status
    movie_id: str
    status: str
    progress: int
    current_step: str | None = None
    video_path: str | None = None
    error: str | None = None
    created_at: str

    # Movie Library information
    prompt: str = ""
    style: str = ""
    language: str = ""
    duration_minutes: int = 0

    # Content settings
    genre: str = ""
    age_group: str = ""
    character_type: str = ""

    # Audio settings
    music_mood: str = ""
    scene_based_music: bool = True
    sound_effects: bool = True

    # Platform settings
    platform: str = ""
    aspect_ratio: str = ""

    # Character settings
    talking_animals: bool = False
    lip_sync: bool = True

    # Accessibility
    subtitles: bool = True

    # Thumbnail settings
    auto_generate_thumbnail: bool = True
    thumbnail_style: str = ""
    thumbnail_title: str = ""
    thumbnail_expression: str = ""
    include_main_character: bool = True

    # Approval workflow
    approval_status: str = "PENDING_REVIEW"
    approval_reason: str | None = None
    reviewed_at: str | None = None
    auto_approved: bool = False
    review_started_at: str | None = None
    auto_approval_at: str | None = None

    # Publishing schedule
    scheduled_at: str | None = None
    scheduled_platform: str | None = None
    scheduled_timezone: str | None = None
    schedule_status: str = "NOT_SCHEDULED"

    # Scene breakdown
    scenes: list[SceneResponse] = []


# ============================================================
# VIDEO BUFFER RESPONSE MODEL
# ============================================================

class BufferStatusResponse(BaseModel):
    ready_videos: int
    minimum_buffer: int = 7
    maximum_buffer: int = 10
    status: str
    videos_needed: int
    queue_refill_required: bool
    queue_refill_status: str
    pending_review: int
    generating: int
    scheduled: int
    approved_not_scheduled: int


# ============================================================
# CONTENT QUEUE RESPONSE MODELS
# ============================================================

class ContentQueueResponse(BaseModel):
    queue_id: str
    status: str
    created_at: str
    buffer_status: str = ""
    videos_needed: int = 0
    prompt: str = ""
    genre: str = ""
    age_group: str = ""
    language: str = ""
    platform: str = ""
    priority: int = 1


class ContentQueueRefillResponse(BaseModel):
    created: int
    active_queue_items: int
    videos_needed: int
    queue_status: str
    items: list[ContentQueueResponse]


# ============================================================
# BUFFER INTELLIGENCE
# ============================================================

def calculate_buffer_status(
    movies: list[dict],
) -> dict:
    ready_videos = 0
    pending_review = 0
    generating = 0
    scheduled = 0
    approved_not_scheduled = 0

    for movie in movies:
        status = str(movie.get("status", "")).lower()
        approval_status = str(
            movie.get("approval_status", "")
        ).upper()
        schedule_status = str(
            movie.get("schedule_status", "NOT_SCHEDULED")
        ).upper()

        if status in {"queued", "processing"}:
            generating += 1

        if (
            status == "completed"
            and approval_status == "PENDING_REVIEW"
        ):
            pending_review += 1

        if schedule_status == "SCHEDULED":
            scheduled += 1

        if (
            status == "completed"
            and approval_status == "APPROVED"
            and schedule_status != "SCHEDULED"
        ):
            ready_videos += 1
            approved_not_scheduled += 1

    if ready_videos < 7:
        buffer_status = "LOW"
        videos_needed = 7 - ready_videos
        queue_refill_required = True
        queue_refill_status = "REFILL_REQUIRED"
    elif ready_videos <= 10:
        buffer_status = "HEALTHY"
        videos_needed = 0
        queue_refill_required = False
        queue_refill_status = "MAINTAIN"
    else:
        buffer_status = "FULL"
        videos_needed = 0
        queue_refill_required = False
        queue_refill_status = "PAUSED"

    return {
        "ready_videos": ready_videos,
        "minimum_buffer": 7,
        "maximum_buffer": 10,
        "status": buffer_status,
        "videos_needed": videos_needed,
        "queue_refill_required": queue_refill_required,
        "queue_refill_status": queue_refill_status,
        "pending_review": pending_review,
        "generating": generating,
        "scheduled": scheduled,
        "approved_not_scheduled": approved_not_scheduled,
    }


# ============================================================
# CONTENT QUEUE RESPONSE MODEL
# ============================================================

class ContentQueueItemResponse(BaseModel):
    queue_id: str
    status: str
    created_at: str
    updated_at: str | None = None
    buffer_reason: str = ""
    queue_position: int = 0
    movie_id: str | None = None
    story_title: str | None = None
    prompt: str | None = None


class ContentQueueRefillResponse(BaseModel):
    created_count: int
    videos_needed: int
    active_queue_items: int
    message: str
    buffer_status: BufferStatusResponse
    created_items: list[ContentQueueItemResponse]


# ============================================================
# QUEUE AUTO STORY REQUEST
# ============================================================

class QueueAutoStoryRequest(BaseModel):
    niche: str = "Auto"
    language: str = "Auto"
    age_group: str = "Auto"


# ============================================================
# QUEUE MOVIE GENERATION REQUEST
# ============================================================

class QueueMovieGenerationRequest(BaseModel):
    style: str = "Auto"
    language: str = "Auto"
    duration_minutes: int = Field(
        default=1,
        ge=1,
        le=30,
    )
    genre: str = "Auto"
    age_group: str = "Auto"
    character_type: str = "Mixed"
    music_mood: str = "Auto"
    platform: str = "YouTube Video"
    aspect_ratio: str = "16:9"
    talking_animals: bool = False
    lip_sync: bool = True
    scene_based_music: bool = True
    sound_effects: bool = True
    subtitles: bool = True
    auto_generate_thumbnail: bool = True
    thumbnail_style: str = "Cinematic"
    thumbnail_title: str = ""
    thumbnail_expression: str = "Excited"
    include_main_character: bool = True


# ============================================================
# SCENE GENERATION ENGINE
# ============================================================

def generate_scenes(
    prompt: str,
    genre: str,
    duration_minutes: int,
    character_type: str,
    music_mood: str,
    sound_effects_enabled: bool,
):
    """
    Temporary MVP scene planning engine.

    Later this will be replaced with the real Aadwik
    AI story and scene planning engine.
    """

    total_seconds = duration_minutes * 60

    scene_count = max(
        5,
        min(
            10,
            duration_minutes + 4,
        ),
    )

    seconds_per_scene = max(
        10,
        total_seconds // scene_count,
    )

    main_character = (
        "Main Character"
        if character_type == "Human"
        else "Main Characters"
    )

    default_music = (
        "Fantasy / Magical"
        if music_mood == "Auto"
        else music_mood
    )

    scenes = [
        {
            "scene_number": 1,
            "title": "The Beginning",
            "description": (
                "The story begins by introducing the world and setting. "
                "The audience is introduced to the main situation from the story: "
                f"{prompt[:250]}"
            ),
            "characters": [
                main_character,
            ],
            "dialogue": (
                "The characters begin their journey and the story world "
                "is introduced."
            ),
            "emotion": "Curiosity",
            "visual_direction": (
                "Create a visually engaging opening that introduces the "
                "environment and main character naturally."
            ),
            "camera_direction": (
                "Wide establishing shot followed by a slow cinematic "
                "push toward the character."
            ),
            "music_mood": default_music,
            "sound_effects": (
                [
                    "Natural ambience",
                    "Gentle environmental sounds",
                ]
                if sound_effects_enabled
                else []
            ),
            "estimated_duration_seconds": (
                seconds_per_scene
            ),
            "status": "PLANNED",
            "production_step": (
                "Scene planning completed."
            ),
            "progress": 0,
        },
        {
            "scene_number": 2,
            "title": "The Discovery",
            "description": (
                "The main character discovers something important that "
                "begins the central adventure or conflict."
            ),
            "characters": [
                main_character,
            ],
            "dialogue": (
                "The character reacts naturally to an unexpected discovery."
            ),
            "emotion": "Surprise",
            "visual_direction": (
                "Focus on the important discovery and show the "
                "character's natural reaction."
            ),
            "camera_direction": (
                "Medium character shot followed by close-up reaction shots."
            ),
            "music_mood": default_music,
            "sound_effects": (
                [
                    "Discovery sound",
                    "Environmental ambience",
                ]
                if sound_effects_enabled
                else []
            ),
            "estimated_duration_seconds": (
                seconds_per_scene
            ),
            "status": "PLANNED",
            "production_step": (
                "Waiting for production."
            ),
            "progress": 0,
        },
        {
            "scene_number": 3,
            "title": "The Challenge",
            "description": (
                "The main character encounters a challenge or obstacle "
                "that must be overcome to continue the journey."
            ),
            "characters": [
                main_character,
            ],
            "dialogue": (
                "The character expresses determination and considers "
                "how to solve the problem."
            ),
            "emotion": "Tension",
            "visual_direction": (
                "Increase visual energy while keeping the scene "
                "emotionally believable."
            ),
            "camera_direction": (
                "Dynamic tracking shots mixed with character close-ups."
            ),
            "music_mood": "Adventure / Tension",
            "sound_effects": (
                [
                    "Movement sounds",
                    "Environmental action sounds",
                ]
                if sound_effects_enabled
                else []
            ),
            "estimated_duration_seconds": (
                seconds_per_scene
            ),
            "status": "PLANNED",
            "production_step": (
                "Waiting for production."
            ),
            "progress": 0,
        },
        {
            "scene_number": 4,
            "title": "The Emotional Moment",
            "description": (
                "The character experiences an important emotional moment "
                "and learns something meaningful from the journey."
            ),
            "characters": [
                main_character,
            ],
            "dialogue": (
                "The character reflects naturally on what has happened "
                "and what it means."
            ),
            "emotion": "Hope",
            "visual_direction": (
                "Use expressive character acting and natural emotional "
                "storytelling."
            ),
            "camera_direction": (
                "Gentle close-ups with slower cinematic movement."
            ),
            "music_mood": "Emotional / Inspiring",
            "sound_effects": (
                [
                    "Soft ambience",
                ]
                if sound_effects_enabled
                else []
            ),
            "estimated_duration_seconds": (
                seconds_per_scene
            ),
            "status": "PLANNED",
            "production_step": (
                "Waiting for production."
            ),
            "progress": 0,
        },
        {
            "scene_number": 5,
            "title": "The Resolution",
            "description": (
                "The main conflict is resolved and the journey reaches "
                "a meaningful conclusion."
            ),
            "characters": [
                main_character,
            ],
            "dialogue": (
                "The characters celebrate or peacefully acknowledge "
                "what they have learned."
            ),
            "emotion": "Joy",
            "visual_direction": (
                "Create a satisfying and visually beautiful conclusion."
            ),
            "camera_direction": (
                "Wide cinematic shot transitioning into a memorable "
                "final frame."
            ),
            "music_mood": (
                "Inspirational / Uplifting"
            ),
            "sound_effects": (
                [
                    "Gentle ambience",
                    "Positive environmental sounds",
                ]
                if sound_effects_enabled
                else []
            ),
            "estimated_duration_seconds": (
                seconds_per_scene
            ),
            "status": "PLANNED",
            "production_step": (
                "Waiting for production."
            ),
            "progress": 0,
        },
    ]

    # Add additional scenes for longer movies
    while len(scenes) < scene_count:
        number = len(scenes) + 1

        scenes.insert(
            -1,
            {
                "scene_number": number,
                "title": (
                    f"Adventure Continues {number - 4}"
                ),
                "description": (
                    "The story continues with new developments, interactions, "
                    "and meaningful progress toward the final resolution."
                ),
                "characters": [
                    main_character,
                ],
                "dialogue": (
                    "The characters continue the story with natural and "
                    "emotionally believable dialogue."
                ),
                "emotion": "Adventure",
                "visual_direction": (
                    "Show new story developments while maintaining "
                    "character and visual consistency."
                ),
                "camera_direction": (
                    "Cinematic tracking and medium character shots."
                ),
                "music_mood": default_music,
                "sound_effects": (
                    [
                        "Environmental ambience",
                        "Story action sounds",
                    ]
                    if sound_effects_enabled
                    else []
                ),
                "estimated_duration_seconds": (
                    seconds_per_scene
                ),
                "status": "PLANNED",
                "production_step": (
                    "Waiting for production."
                ),
                "progress": 0,
            },
        )

    # Re-number scenes
    for index, scene in enumerate(
        scenes,
        start=1,
    ):
        scene["scene_number"] = index

    return scenes


# ============================================================
# UPDATE SCENE PRODUCTION STATUS
# ============================================================

def update_scene_production_status(
    scenes: list[dict],
    movie_progress: int,
):
    """
    Maps overall movie progress to scene production status.

    Later this will be replaced by actual independent AI jobs
    for each scene.
    """

    updated_scenes = []

    total_scenes = max(
        1,
        len(scenes),
    )

    progress_per_scene = (
        100 / total_scenes
    )

    for scene in scenes:
        scene_copy = dict(scene)

        scene_number = scene_copy[
            "scene_number"
        ]

        scene_start = (
            (scene_number - 1)
            * progress_per_scene
        )

        scene_end = (
            scene_number
            * progress_per_scene
        )

        if movie_progress >= 100:
            scene_copy["status"] = (
                "COMPLETED"
            )
            scene_copy["production_step"] = (
                "Scene fully completed and included in the final movie."
            )
            scene_copy["progress"] = 100

        elif movie_progress >= scene_end:
            scene_copy["status"] = (
                "RENDERED"
            )
            scene_copy["production_step"] = (
                "Scene rendered and ready for final composition."
            )
            scene_copy["progress"] = 100

        elif movie_progress >= (
            scene_start
            + progress_per_scene * 0.7
        ):
            scene_copy["status"] = (
                "GENERATING"
            )
            scene_copy["production_step"] = (
                "Generating animation, voice, music and sound."
            )
            scene_copy["progress"] = 70

        elif movie_progress >= (
            scene_start
            + progress_per_scene * 0.35
        ):
            scene_copy["status"] = (
                "ASSETS_READY"
            )
            scene_copy["production_step"] = (
                "Character references and visual assets prepared."
            )
            scene_copy["progress"] = 35

        elif movie_progress >= scene_start:
            scene_copy["status"] = (
                "PLANNED"
            )
            scene_copy["production_step"] = (
                "Scene planned and waiting for production."
            )
            scene_copy["progress"] = 10

        else:
            scene_copy["status"] = (
                "PLANNED"
            )
            scene_copy["production_step"] = (
                "Waiting for production."
            )
            scene_copy["progress"] = 0

        updated_scenes.append(
            scene_copy
        )

    return updated_scenes


# ============================================================
# GET CURRENT PIPELINE STEP
# ============================================================

def get_pipeline_step(
    progress: int,
):
    stages = [
        (
            10,
            "Planning story and scenes.",
        ),
        (
            25,
            "Creating character references.",
        ),
        (
            45,
            "Generating animated shots.",
        ),
        (
            65,
            "Generating voice and dialogue.",
        ),
        (
            80,
            "Adding music and audio.",
        ),
        (
            95,
            "Composing final movie.",
        ),
        (
            99,
            "Finalizing movie.",
        ),
    ]

    for threshold, text in stages:
        if progress <= threshold:
            return text

    return "Finalizing movie."


# ============================================================
# SYNC CONTENT QUEUE WITH MOVIE STATUS
# ============================================================

def update_queue_for_movie(
    movie_id: str,
    status: str,
):
    for item in content_queue_store.list():
        if item.get("movie_id") == movie_id:
            return content_queue_store.update(
                item["queue_id"],
                status=status,
                updated_at=datetime.now(
                    timezone.utc
                ).isoformat(),
            )

    return None


# ============================================================
# BACKGROUND GENERATION PIPELINE
# ============================================================

def run_movie_generation(movie_id: str):
    """
    Real Aadwik local production pipeline.

    Story
        -> LocalVideoProvider
        -> Blender 3D
        -> PNG frames
        -> FFmpeg
        -> verified MP4
        -> review queue
    """

    try:
        movie = store.get(movie_id)

        if not movie:
            print(
                f"[AADWIK MOVIE] Movie not found: {movie_id}",
                flush=True,
            )
            return

        if movie.get("status") == "cancelled":
            return

        # -------------------------------------------------
        # PREPARE
        # -------------------------------------------------

        store.update(
            movie_id,
            status="processing",
            progress=5,
            current_step="Preparing Aadwik local 3D production.",
        )

        backend_dir = Path(__file__).resolve().parents[2]
        generated_dir = backend_dir / "generated"

        generated_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = (
            generated_dir / f"{movie_id}.mp4"
        )

        # -------------------------------------------------
        # MARK STORY / SCENES READY
        # -------------------------------------------------

        movie = store.get(movie_id)

        if not movie:
            return

        if movie.get("status") == "cancelled":
            return

        planned_scenes = update_scene_production_status(
            movie.get("scenes", []),
            15,
        )

        store.update(
            movie_id,
            status="processing",
            progress=15,
            current_step="Story and scene plan ready.",
            scenes=planned_scenes,
        )

        # -------------------------------------------------
        # REAL BLENDER GENERATION
        # -------------------------------------------------

        store.update(
            movie_id,
            status="processing",
            progress=20,
            current_step="Rendering Aadwik 3D movie with Blender.",
        )

        provider = LocalVideoProvider()

        provider.generate_video(
            prompt=movie.get(
                "prompt",
                "",
            ),
            output_path=output_path,
            aspect_ratio=movie.get(
                "aspect_ratio",
                "16:9",
            ),
            style=movie.get(
                "style",
                "stylized cinematic 3D",
            ),
        )

        # -------------------------------------------------
        # CHECK CANCELLATION
        # -------------------------------------------------

        movie = store.get(movie_id)

        if not movie:
            return

        if movie.get("status") == "cancelled":
            return

        # -------------------------------------------------
        # VERIFY FINAL MP4
        # -------------------------------------------------

        store.update(
            movie_id,
            status="processing",
            progress=95,
            current_step="Verifying final movie.",
        )

        if not output_path.exists():
            raise RuntimeError(
                "Local video generation completed but "
                "the MP4 file was not created."
            )

        if output_path.stat().st_size <= 0:
            raise RuntimeError(
                "Local video generation created "
                "an empty MP4 file."
            )

        # -------------------------------------------------
        # COMPLETE SCENES
        # -------------------------------------------------

        completed_scenes = (
            update_scene_production_status(
                movie.get(
                    "scenes",
                    [],
                ),
                100,
            )
        )

        # -------------------------------------------------
        # REVIEW WINDOW
        # -------------------------------------------------

        review_started_at = datetime.now(
            timezone.utc,
        )

        auto_approval_hours = random.randint(
            48,
            72,
        )

        auto_approval_at = (
            review_started_at
            + timedelta(
                hours=auto_approval_hours,
            )
        )

        # -------------------------------------------------
        # COMPLETE MOVIE
        # -------------------------------------------------

        store.update(
            movie_id,
            status="completed",
            progress=100,
            current_step=(
                "Movie generation completed. "
                "Waiting for manual review."
            ),
            video_path=(
                f"/generated/{movie_id}.mp4"
            ),
            error=None,
            scenes=completed_scenes,
            approval_status="PENDING_REVIEW",
            approval_reason=None,
            reviewed_at=None,
            auto_approved=False,
            review_started_at=(
                review_started_at.isoformat()
            ),
            auto_approval_at=(
                auto_approval_at.isoformat()
            ),
        )

        # -------------------------------------------------
        # CONTENT QUEUE
        # -------------------------------------------------

        update_queue_for_movie(
            movie_id,
            "PENDING_REVIEW",
        )

        print(
            f"[AADWIK MOVIE] REAL PRODUCTION SUCCESS: "
            f"{movie_id}",
            flush=True,
        )

    except Exception as exc:

        import traceback

        print(
            "\n" + "=" * 70,
            flush=True,
        )

        print(
            "[AADWIK MOVIE ERROR]",
            flush=True,
        )

        print(
            f"Movie ID: {movie_id}",
            flush=True,
        )

        print(
            f"Error type: {type(exc).__name__}",
            flush=True,
        )

        print(
            f"Error message: {str(exc)}",
            flush=True,
        )

        traceback.print_exc()

        print(
            "=" * 70 + "\n",
            flush=True,
        )

        movie = store.get(movie_id)

        if (
            movie
            and movie.get("status") != "cancelled"
        ):
            store.update(
                movie_id,
                status="failed",
                progress=0,
                current_step=(
                    "Movie generation failed."
                ),
                error=(
                    f"{type(exc).__name__}: "
                    f"{str(exc)}"
                ),
            )

            update_queue_for_movie(
                movie_id,
                "WAITING_FOR_GENERATION",
            )
# ============================================================
# CREATE MOVIE
# ============================================================

@router.post(
    "",
    response_model=MovieResponse,
)
def create_movie(
    payload: CreateMovieRequest,
    background_tasks: BackgroundTasks,
):
    if payload.style not in (
        settings.allowed_styles
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "Unsupported animation style"
            ),
        )

    if payload.language not in (
        settings.allowed_languages
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "Unsupported language"
            ),
        )

    movie_id = str(
        uuid4()
    )

    scenes = generate_scenes(
        prompt=payload.prompt,
        genre=payload.genre,
        duration_minutes=(
            payload.duration_minutes
        ),
        character_type=(
            payload.character_type
        ),
        music_mood=(
            payload.music_mood
        ),
        sound_effects_enabled=(
            payload.sound_effects
        ),
    )

    movie = {
        "movie_id": movie_id,
        "status": "queued",
        "progress": 1,
        "current_step": (
            "Story received. Planning scenes."
        ),
        "video_path": None,
        "error": None,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),

        # Story
        "prompt": payload.prompt,

        # Basic settings
        "style": payload.style,
        "language": payload.language,
        "duration_minutes": (
            payload.duration_minutes
        ),

        # Content settings
        "genre": payload.genre,
        "age_group": (
            payload.age_group
        ),
        "character_type": (
            payload.character_type
        ),

        # Audio settings
        "music_mood": (
            payload.music_mood
        ),
        "scene_based_music": (
            payload.scene_based_music
        ),
        "sound_effects": (
            payload.sound_effects
        ),

        # Platform
        "platform": (
            payload.platform
        ),
        "aspect_ratio": (
            payload.aspect_ratio
        ),

        # Character settings
        "talking_animals": (
            payload.talking_animals
        ),
        "lip_sync": (
            payload.lip_sync
        ),

        # Accessibility
        "subtitles": (
            payload.subtitles
        ),

        # Thumbnail settings
        "auto_generate_thumbnail": (
            payload.auto_generate_thumbnail
        ),
        "thumbnail_style": (
            payload.thumbnail_style
        ),
        "thumbnail_title": (
            payload.thumbnail_title
        ),
        "thumbnail_expression": (
            payload.thumbnail_expression
        ),
        "include_main_character": (
            payload.include_main_character
        ),

        # Approval workflow
        "approval_status": "PENDING_REVIEW",
        "approval_reason": None,
        "reviewed_at": None,
        "auto_approved": False,
        "review_started_at": None,
        "auto_approval_at": None,

        # Publishing schedule
        "scheduled_at": None,
        "scheduled_platform": None,
        "scheduled_timezone": None,
        "schedule_status": "NOT_SCHEDULED",

        # Scene Breakdown
        "scenes": scenes,
    }

    created_movie = store.create(
        movie
    )

    # Start generation independently
    # of frontend polling
    background_tasks.add_task(
        run_movie_generation,
        movie_id,
    )

    return created_movie


# ============================================================
# SAFE CONFIGURATION DEFAULT HELPER
# ============================================================

def first_allowed_value(values):
    values_list = list(values)

    if not values_list:
        raise HTTPException(
            status_code=500,
            detail="Aadwik configuration has no allowed values configured.",
        )

    return values_list[0]


# ============================================================
# GENERATE MOVIE FROM CONTENT QUEUE
# ============================================================

@router.post(
    "/content-queue/{queue_id}/generate-movie",
    response_model=MovieResponse,
)
def generate_movie_from_content_queue(
    queue_id: str,
    payload: QueueMovieGenerationRequest,
    background_tasks: BackgroundTasks,
):
    queue_item = content_queue_store.get(
        queue_id
    )

    if not queue_item:
        raise HTTPException(
            status_code=404,
            detail="Content queue item not found.",
        )

    if queue_item.get("status") != "WAITING_FOR_GENERATION":
        raise HTTPException(
            status_code=400,
            detail=(
                "Movie generation can only start for items "
                "with WAITING_FOR_GENERATION status."
            ),
        )

    prompt = (
        queue_item.get("prompt")
        or ""
    ).strip()

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail=(
                "Queue item has no story prompt. "
                "Generate the Auto Story first."
            ),
        )

    try:
        style = payload.style
        if style == "Auto":
            style = first_allowed_value(
                settings.allowed_styles
            )

        language = payload.language
        if language == "Auto":
            queue_language = (
                queue_item.get("language")
                or "English"
            )

            if queue_language in settings.allowed_languages:
                language = queue_language
            else:
                language = first_allowed_value(
                    settings.allowed_languages
                )

        genre = payload.genre
        if genre == "Auto":
            genre = (
                queue_item.get("genre")
                or "Fantasy"
            )

        age_group = payload.age_group
        if age_group == "Auto":
            age_group = (
                queue_item.get("age_group")
                or "All Ages"
            )

        title = (
            payload.thumbnail_title.strip()
            or queue_item.get("story_title")
            or ""
        )

        movie_payload = CreateMovieRequest(
            prompt=prompt,
            style=style,
            language=language,
            duration_minutes=(
                payload.duration_minutes
            ),
            genre=genre,
            age_group=age_group,
            character_type=(
                payload.character_type
            ),
            music_mood=(
                payload.music_mood
            ),
            scene_based_music=(
                payload.scene_based_music
            ),
            sound_effects=(
                payload.sound_effects
            ),
            platform=payload.platform,
            aspect_ratio=(
                payload.aspect_ratio
            ),
            talking_animals=(
                payload.talking_animals
            ),
            lip_sync=payload.lip_sync,
            subtitles=payload.subtitles,
            auto_generate_thumbnail=(
                payload.auto_generate_thumbnail
            ),
            thumbnail_style=(
                payload.thumbnail_style
            ),
            thumbnail_title=title,
            thumbnail_expression=(
                payload.thumbnail_expression
            ),
            include_main_character=(
                payload.include_main_character
            ),
        )

        # Create the movie first. This keeps the queue unchanged
        # if movie creation itself fails.
        created_movie = create_movie(
            movie_payload,
            background_tasks,
        )

        content_queue_store.update(
            queue_id,
            movie_id=(
                created_movie["movie_id"]
            ),
            status="GENERATING",
            updated_at=datetime.now(
                timezone.utc
            ).isoformat(),
        )

        return created_movie

    except HTTPException:
        raise

    except Exception as exc:
        content_queue_store.update(
            queue_id,
            status="WAITING_FOR_GENERATION",
            updated_at=datetime.now(
                timezone.utc
            ).isoformat(),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Queue movie generation failed: "
                f"{type(exc).__name__}: {str(exc)}"
            ),
        )


# ============================================================
# LIST MOVIES
# ============================================================

@router.get(
    "",
    response_model=list[MovieResponse],
)
def list_movies():
    return store.list()


# ============================================================
# GET VIDEO BUFFER STATUS
# ============================================================

@router.get(
    "/buffer-status",
    response_model=BufferStatusResponse,
)
def get_buffer_status():
    """
    Aadwik 7-10 video buffer intelligence endpoint.

    This version calculates refill requirements safely.
    It does not automatically generate unlimited movies.
    """

    return calculate_buffer_status(
        store.list()
    )


# ============================================================
# LIST CONTENT QUEUE
# ============================================================

@router.get(
    "/content-queue",
    response_model=list[ContentQueueItemResponse],
)
def list_content_queue():
    return content_queue_store.list()


# ============================================================
# REFILL CONTENT QUEUE
# ============================================================

@router.post(
    "/content-queue/refill",
    response_model=ContentQueueRefillResponse,
)
def refill_content_queue():
    """
    Creates only the queue items currently required to restore
    the Aadwik ready-video buffer to its minimum target of 7.

    Existing active queue items are counted so repeated calls do
    not create duplicate refill requirements.
    """

    buffer_data = calculate_buffer_status(
        store.list()
    )

    videos_needed = buffer_data[
        "videos_needed"
    ]

    active_queue_items = (
        content_queue_store.count_active()
    )

    items_to_create = max(
        0,
        videos_needed - active_queue_items,
    )

    created_items = []

    for index in range(
        items_to_create
    ):
        now = datetime.now(
            timezone.utc
        ).isoformat()

        queue_id = (
            f"queue_{uuid4().hex}"
        )

        item = {
            "queue_id": queue_id,
            "status": "WAITING_FOR_STORY",
            "created_at": now,
            "updated_at": now,
            "buffer_reason": (
                "Automatic refill required "
                "to maintain the 7-video "
                "minimum ready buffer."
            ),
            "queue_position": (
                active_queue_items
                + index
                + 1
            ),
            "movie_id": None,
            "story_title": None,
            "prompt": None,
        }

        created_items.append(
            content_queue_store.create(
                item
            )
        )

    if items_to_create > 0:
        message = (
            f"Created {items_to_create} "
            f"queue item(s) for buffer refill."
        )
    elif videos_needed <= 0:
        message = (
            "Buffer is already healthy. "
            "No refill is required."
        )
    else:
        message = (
            "Existing active queue items "
            "already cover the refill requirement."
        )

    return {
        "created_count": items_to_create,
        "videos_needed": videos_needed,
        "active_queue_items": active_queue_items,
        "message": message,
        "buffer_status": buffer_data,
        "created_items": created_items,
    }


# ============================================================
# GENERATE AUTO STORY FOR CONTENT QUEUE ITEM
# ============================================================

@router.post(
    "/content-queue/{queue_id}/auto-story",
    response_model=ContentQueueItemResponse,
)
def generate_queue_auto_story(
    queue_id: str,
    payload: QueueAutoStoryRequest,
):
    queue_item = content_queue_store.get(queue_id)

    if not queue_item:
        raise HTTPException(
            status_code=404,
            detail="Content queue item not found.",
        )

    generated_story = generate_random_story(
        payload.niche
    )

    title = generated_story["title"]
    story = generated_story["story"]

    now = datetime.now(
        timezone.utc
    ).isoformat()

    updated_item = content_queue_store.update(
        queue_id,
        status="WAITING_FOR_GENERATION",
        updated_at=now,
        story_title=title,
        prompt=story,
        niche=payload.niche,
        language=payload.language,
        age_group=payload.age_group,
        genre=generated_story["genre"],
    )

    return updated_item


# ============================================================
# GET MOVIE STATUS
# ============================================================

@router.get(
    "/{movie_id}",
    response_model=MovieResponse,
)
def get_movie(
    movie_id: str,
):
    movie = store.get(
        movie_id
    )

    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found",
        )

    # IMPORTANT:
    # This endpoint now ONLY READS status.
    # It does NOT advance generation.

    return movie


# ============================================================
# CANCEL MOVIE
# ============================================================

@router.post(
    "/{movie_id}/cancel",
    response_model=MovieResponse,
)
def cancel_movie(
    movie_id: str,
):
    movie = store.get(
        movie_id
    )

    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found",
        )

    if movie.get(
        "status"
    ) == "completed":
        raise HTTPException(
            status_code=400,
            detail=(
                "Completed movies cannot be cancelled."
            ),
        )

    if movie.get(
        "status"
    ) == "cancelled":
        return movie

    return store.update(
        movie_id,
        status="cancelled",
        current_step=(
            "Generation cancelled by user."
        ),
    )


# ============================================================
# MOVIE APPROVAL
# ============================================================

@router.post(
    "/{movie_id}/approval",
    response_model=MovieResponse,
)
def approve_movie(
    movie_id: str,
    payload: ApprovalRequest,
):
    movie = store.get(
        movie_id
    )

    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found",
        )

    if movie.get(
        "status"
    ) != "completed":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only completed movies can be reviewed."
            ),
        )

    action = payload.action.upper().strip()

    if action not in {
        "APPROVE",
        "NEEDS_REVIEW",
        "REJECT",
    }:
        raise HTTPException(
            status_code=422,
            detail=(
                "Invalid approval action. "
                "Use APPROVE, NEEDS_REVIEW, or REJECT."
            ),
        )

    approval_status = {
        "APPROVE": "APPROVED",
        "NEEDS_REVIEW": "NEEDS_REVIEW",
        "REJECT": "REJECTED",
    }[action]

    return store.update(
        movie_id,
        approval_status=approval_status,
        approval_reason=(
            payload.reason
        ),
        reviewed_at=datetime.now(
            timezone.utc
        ).isoformat(),
        auto_approved=False,
        auto_approval_at=None,
    )


# ============================================================
# SCHEDULE MOVIE
# ============================================================

@router.post(
    "/{movie_id}/schedule",
    response_model=MovieResponse,
)
def schedule_movie(
    movie_id: str,
    payload: ScheduleMovieRequest,
):
    movie = store.get(
        movie_id
    )

    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found",
        )

    if movie.get(
        "status"
    ) != "completed":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only completed movies can be scheduled."
            ),
        )

    if movie.get(
        "approval_status"
    ) != "APPROVED":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only approved movies can be scheduled."
            ),
        )

    try:
        scheduled_datetime = (
            datetime.fromisoformat(
                payload.scheduled_at.replace(
                    "Z",
                    "+00:00",
                )
            )
        )
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=(
                "Invalid scheduled_at datetime format."
            ),
        )

    if (
        scheduled_datetime.tzinfo is not None
    ):
        now = datetime.now(
            timezone.utc
        )

        if (
            scheduled_datetime.astimezone(
                timezone.utc
            )
            <= now
        ):
            raise HTTPException(
                status_code=422,
                detail=(
                    "Scheduled time must be in the future."
                ),
            )
    else:
        if scheduled_datetime <= datetime.now():
            raise HTTPException(
                status_code=422,
                detail=(
                    "Scheduled time must be in the future."
                ),
            )

    return store.update(
        movie_id,
        scheduled_at=(
            payload.scheduled_at
        ),
        scheduled_platform=(
            payload.platform
        ),
        scheduled_timezone=(
            payload.timezone
        ),
        schedule_status="SCHEDULED",
        current_step=(
            "Movie scheduled for publishing."
        ),
    )


# ============================================================
# AUTO STORY
# ============================================================

@router.post(
    "/auto-story",
    response_model=AutoStoryResponse,
)
def auto_story(
    payload: AutoStoryRequest,
):
    generated_story = generate_random_story(
        payload.niche
    )

    return AutoStoryResponse(
        title=generated_story["title"],
        story=generated_story["story"],
        genre=generated_story["genre"],
        age_group="All Ages",
        recommended_style=(
            generated_story[
                "recommended_style"
            ]
        ),
        character_type=(
            generated_story[
                "character_type"
            ]
        ),
        music_mood=(
            generated_story[
                "music_mood"
            ]
        ),
        talking_animals=(
            generated_story[
                "talking_animals"
            ]
        ),
    )