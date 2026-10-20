from dataclasses import dataclass, field

@dataclass
class ContinuityIssue:
    kind: str
    severity: str
    message: str
    entity_id: str = ""

@dataclass
class ContinuityReport:
    passed: bool
    issues: list = field(default_factory=list)

def validate_scene(scene, locked_character_ids=None, locked_world_ids=None):
    locked_character_ids = set(locked_character_ids or [])
    locked_world_ids = set(locked_world_ids or [])
    issues = []
    for cid in scene.get("characters", []) or []:
        value = cid if isinstance(cid, str) else cid.get("character_id") or cid.get("id")
        if value and locked_character_ids and value not in locked_character_ids:
            issues.append(ContinuityIssue("character", "HIGH",
                f"Character '{value}' is not in the locked character set.", str(value)))
    for wid in scene.get("locations", []) or scene.get("worlds", []) or []:
        value = wid if isinstance(wid, str) else wid.get("world_id") or wid.get("id")
        if value and locked_world_ids and value not in locked_world_ids:
            issues.append(ContinuityIssue("world", "HIGH",
                f"World '{value}' is not in the locked world set.", str(value)))
    return ContinuityReport(not issues, issues)

def validate_shot(shot, scene):
    issues=[]
    if shot.get("scene_number") != scene.get("scene_number"):
        issues.append(ContinuityIssue("scene_reference","HIGH",
            "Shot scene reference does not match its scene."))
    for key in ("characters","locations","props"):
        if key in shot and key in scene:
            scene_values = {x if isinstance(x,str) else x.get("id") or x.get("character_id") or x.get("world_id")
                            for x in (scene.get(key) or [])}
            for x in shot.get(key) or []:
                value = x if isinstance(x,str) else x.get("id") or x.get("character_id") or x.get("world_id")
                if value and scene_values and value not in scene_values:
                    issues.append(ContinuityIssue(key,"MEDIUM",
                        f"Shot references '{value}' not present in scene.",str(value)))
    return ContinuityReport(not issues, issues)
