from app.core.continuity import validate_scene, validate_shot

def create_character_lock(character):
    data=dict(character)
    data["identity_locked"]=True
    data.setdefault("design_version","v1")
    data.setdefault("continuity_rules",[])
    return data

def create_world_lock(world):
    data=dict(world)
    data["identity_locked"]=True
    data.setdefault("visual_style","cinematic_stylized_3d")
    data.setdefault("continuity_rules",[])
    return data

def lock_story_bible(story_bible):
    bible=dict(story_bible)
    bible["characters"]=[create_character_lock(x) if isinstance(x,dict) else x
                         for x in bible.get("characters",[])]
    bible["worlds"]=[create_world_lock(x) if isinstance(x,dict) else x
                     for x in bible.get("worlds",[])]
    bible["locked"]=True
    return bible

def validate_story_continuity(story_bible, scenes, shots):
    char_ids={x.get("character_id") or x.get("id") or x.get("name")
              for x in story_bible.get("characters",[]) if isinstance(x,dict)}
    world_ids={x.get("world_id") or x.get("id") or x.get("name")
               for x in story_bible.get("worlds",[]) if isinstance(x,dict)}
    issues=[]
    for scene in scenes:
        report=validate_scene(scene,char_ids,world_ids)
        issues.extend(report.issues)
    scene_map={s.get("scene_number"):s for s in scenes}
    for shot in shots:
        scene=scene_map.get(shot.get("scene_number"))
        if scene:
            issues.extend(validate_shot(shot,scene).issues)
    return {"passed":not issues,"issues":[i.__dict__ for i in issues]}

def repair_recommendations(report):
    recommendations=[]
    for issue in report.get("issues",[]):
        if issue["kind"]=="character":
            recommendations.append(f"Restore locked character '{issue['entity_id']}' or explicitly update the Story Bible.")
        elif issue["kind"]=="world":
            recommendations.append(f"Restore locked world '{issue['entity_id']}' or explicitly update the Story Bible.")
        elif issue["kind"]=="scene_reference":
            recommendations.append("Re-map the shot to its correct scene before generation.")
        else:
            recommendations.append(f"Review {issue['kind']} continuity for '{issue['entity_id']}'.")
    return recommendations
