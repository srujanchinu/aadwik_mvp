import os

class Settings:
    app_name = os.getenv("APP_NAME", "Aadwik AI")
    max_duration_minutes = int(os.getenv("MAX_DURATION_MINUTES", "30"))
    allowed_styles = {"Auto Smart Style","3D Animation", "Cartoon", "Anime", "Cinematic Animation"}
    allowed_languages = {"Auto",
    "English",
    "Hindi",
    "Telugu",
    "Tamil",
    "Kannada",
    "Malayalam",
    "Bengali",
    "Marathi",
    "Gujarati",
    "Punjabi",
    "Urdu",
    "Spanish",
    "French",
    "German",
    "Portuguese",
    "Italian",
    "Russian",
    "Arabic",
    "Chinese",
    "Japanese",
    "Korean",
    "Indonesian",
    "Turkish",
    "Dutch",
    "Polish",
    "Vietnamese",
    "Thai",
    "Swedish",
    "Greek"}

settings = Settings()
