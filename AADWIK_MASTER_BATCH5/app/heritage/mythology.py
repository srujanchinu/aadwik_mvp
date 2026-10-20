HERITAGE_CATEGORIES = [
    "Ramayana","Mahabharatham","Krishna","Rama","Shiva","Ganesha",
    "Indian heritage","Freedom fighters","Regional culture"
]

def build_heritage_content_plan(subject, language="English", audience="General"):
    if not subject:
        raise ValueError("Subject is required.")
    return {
        "subject":subject,
        "language":language,
        "audience":audience,
        "respect_cultural_context":True,
        "avoid_distortion":True,
        "story_first":True,
        "categories":list(HERITAGE_CATEGORIES),
    }

def validate_heritage_plan(plan):
    required=("subject","language","audience")
    return {"passed":all(plan.get(x) for x in required)}
