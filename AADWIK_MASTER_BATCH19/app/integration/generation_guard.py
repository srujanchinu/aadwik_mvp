from dataclasses import dataclass
from typing import List

@dataclass
class GuardDecision:
    allowed: bool
    reasons: List[str]

class GenerationGuard:
    def check(self, movie_id, prompt, output_path, enabled=True):
        reasons = []
        if not enabled:
            reasons.append("generation_disabled")
        if not movie_id:
            reasons.append("missing_movie_id")
        if not prompt:
            reasons.append("missing_prompt")
        if not output_path:
            reasons.append("missing_output_path")
        return GuardDecision(not reasons, reasons)
