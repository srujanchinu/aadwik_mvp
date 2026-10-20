from pathlib import Path
import asyncio
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.movies import router as movies_router
from app.services.movie_store import store


app = FastAPI(
    title="Aadwik AI Movie Generator",
)


# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# GENERATED VIDEO FOLDER
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
GENERATED_DIR = BASE_DIR / "generated"

GENERATED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ==========================================================
# SERVE GENERATED VIDEOS
# ==========================================================

app.mount(
    "/generated",
    StaticFiles(
        directory=str(
            GENERATED_DIR,
        ),
    ),
    name="generated",
)


# ==========================================================
# API ROUTES
# ==========================================================

app.include_router(
    movies_router,
)


# ==========================================================
# DATETIME PARSER
# ==========================================================

def parse_datetime(
    value,
):
    if not value:
        return None

    try:
        value = str(value)

        # Support ISO timestamps ending with Z
        if value.endswith("Z"):
            value = (
                value[:-1]
                + "+00:00"
            )

        parsed = datetime.fromisoformat(
            value,
        )

        # If old data has no timezone,
        # treat it as UTC.
        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc,
            )

        return parsed

    except (
        ValueError,
        TypeError,
    ):
        return None


# ==========================================================
# AUTO APPROVAL CHECK
# ==========================================================

def check_auto_approvals():
    """
    Automatically approve movies whose
    auto_approval_at time has arrived.

    Safety rules:
    - Only PENDING_REVIEW movies qualify.
    - NEEDS_REVIEW never auto-approves.
    - REJECTED never auto-approves.
    - Already approved movies are untouched.
    """

    now = datetime.now(
        timezone.utc,
    )

    movies = store.list()

    for movie in movies:

        movie_id = movie.get(
            "movie_id",
        )

        if not movie_id:
            continue

        approval_status = str(
            movie.get(
                "approval_status",
                "",
            )
        ).upper().strip()

        # ==================================================
        # ONLY PENDING REVIEW MOVIES CAN AUTO-APPROVE
        # ==================================================

        if approval_status != "PENDING_REVIEW":
            continue

        auto_approval_at = (
            movie.get(
                "auto_approval_at",
            )
        )

        scheduled_time = parse_datetime(
            auto_approval_at,
        )

        # No auto approval time assigned yet
        if scheduled_time is None:
            continue

        # Review window has not finished yet
        if now < scheduled_time:
            continue

        # ==================================================
        # AUTO APPROVE
        # ==================================================

        store.update(
            movie_id,

            approval_status="APPROVED",

            auto_approved=True,

            approval_reason=(
                "Automatically approved "
                "after the 48–72 hour "
                "manual review window."
            ),

            approved_at=(
                now.isoformat()
            ),

            ready_for_schedule=True,

            schedule_status=(
                "READY_FOR_SCHEDULE"
            ),
        )

        print(
            f"[AUTO APPROVAL] "
            f"Movie {movie_id} "
            f"automatically approved."
        )


# ==========================================================
# BACKGROUND AUTO APPROVAL LOOP
# ==========================================================

async def auto_approval_loop():

    print(
        "[AUTO APPROVAL] "
        "Background checker started."
    )

    while True:

        try:
            check_auto_approvals()

        except Exception as error:

            # Never crash the backend
            # because of one movie.
            print(
                "[AUTO APPROVAL ERROR]",
                error,
            )

        # Check every 5 minutes.
        await asyncio.sleep(
            300,
        )


# ==========================================================
# APPLICATION STARTUP
# ==========================================================

@app.on_event(
    "startup",
)
async def startup_event():

    asyncio.create_task(
        auto_approval_loop(),
    )


# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
def root():
    return {
        "message":
            "Aadwik backend is running",
    }