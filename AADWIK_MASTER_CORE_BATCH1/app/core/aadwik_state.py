from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc).isoformat()

class ProductionState(str, Enum):
    DRAFT='DRAFT'; STORY_LOCKED='STORY_LOCKED'; SCENES_LOCKED='SCENES_LOCKED'; SHOTS_LOCKED='SHOTS_LOCKED'
    IN_PRODUCTION='IN_PRODUCTION'; VISUAL_REVIEW='VISUAL_REVIEW'; AUDIO_REVIEW='AUDIO_REVIEW'; ASSEMBLY='ASSEMBLY'
    FINAL_REVIEW='FINAL_REVIEW'; APPROVED='APPROVED'; PUBLISHED='PUBLISHED'; FAILED='FAILED'; CANCELLED='CANCELLED'

ALLOWED_TRANSITIONS = {
    ProductionState.DRAFT:{ProductionState.STORY_LOCKED,ProductionState.CANCELLED},
    ProductionState.STORY_LOCKED:{ProductionState.SCENES_LOCKED,ProductionState.FAILED,ProductionState.CANCELLED},
    ProductionState.SCENES_LOCKED:{ProductionState.SHOTS_LOCKED,ProductionState.FAILED,ProductionState.CANCELLED},
    ProductionState.SHOTS_LOCKED:{ProductionState.IN_PRODUCTION,ProductionState.FAILED,ProductionState.CANCELLED},
    ProductionState.IN_PRODUCTION:{ProductionState.VISUAL_REVIEW,ProductionState.FAILED,ProductionState.CANCELLED},
    ProductionState.VISUAL_REVIEW:{ProductionState.AUDIO_REVIEW,ProductionState.IN_PRODUCTION,ProductionState.FAILED},
    ProductionState.AUDIO_REVIEW:{ProductionState.ASSEMBLY,ProductionState.FAILED},
    ProductionState.ASSEMBLY:{ProductionState.FINAL_REVIEW,ProductionState.FAILED},
    ProductionState.FINAL_REVIEW:{ProductionState.APPROVED,ProductionState.ASSEMBLY,ProductionState.FAILED},
    ProductionState.APPROVED:{ProductionState.PUBLISHED}, ProductionState.PUBLISHED:set(),
    ProductionState.FAILED:{ProductionState.DRAFT,ProductionState.STORY_LOCKED,ProductionState.CANCELLED},
    ProductionState.CANCELLED:set(),
}

@dataclass
class ProductionStateRecord:
    state: ProductionState = ProductionState.DRAFT
    progress: float = 0.0
    updated_at: str = field(default_factory=utc_now)
    error: str | None = None

    def transition(self, new_state, progress=None, error=None):
        if new_state != self.state and new_state not in ALLOWED_TRANSITIONS[self.state]:
            raise ValueError(f'Invalid production transition: {self.state} -> {new_state}')
        self.state = new_state
        if progress is not None: self.progress = max(0.0, min(100.0, float(progress)))
        self.error = error
        self.updated_at = utc_now()
        return self
