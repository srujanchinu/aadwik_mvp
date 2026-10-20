from app.core.project_context import CharacterLock, WorldLock
def lock_character(data):
    cid=str(data.get('character_id') or data.get('id') or data.get('name') or 'character')
    return CharacterLock(cid,str(data.get('name') or cid),data.get('age'),data.get('appearance',{}) or {},data.get('clothing',{}) or {},data.get('personality',[]) or [],data.get('voice_profile',{}) or {},True)
def lock_world(data):
    wid=str(data.get('world_id') or data.get('id') or data.get('name') or 'world')
    return WorldLock(wid,str(data.get('name') or wid),data.get('environment',{}) or {},str(data.get('visual_style') or 'cinematic_stylized_3d'),data.get('continuity_rules',[]) or [],True)
