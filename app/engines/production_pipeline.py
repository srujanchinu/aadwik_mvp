from app.core.pipeline import build_pipeline

def lock_scenes(scenes):
    result=[]
    for scene in scenes:
        item=dict(scene)
        item["continuity_locked"]=True
        item["status"]="LOCKED"
        result.append(item)
    return result

def lock_shots(shots):
    result=[]
    for shot in shots:
        item=dict(shot)
        item["continuity_locked"]=True
        item["production_status"]="LOCKED"
        result.append(item)
    return result

def create_production_manifest(project_id, story, scenes, shots):
    locked_scenes=lock_scenes(scenes)
    locked_shots=lock_shots(shots)
    ctx=build_pipeline(project_id,story,locked_scenes,locked_shots)
    ctx.status="READY_FOR_PRODUCTION"
    ctx.checkpoint("assets_and_continuity_locked")
    return {
        "project_id":project_id,
        "story":story,
        "scenes":locked_scenes,
        "shots":locked_shots,
        "status":ctx.status,
        "checkpoints":ctx.checkpoints,
    }
