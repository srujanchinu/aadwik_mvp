def build_context(project, story_bible=None, character_memory=None):
    return {"project_id":project,"story_bible":story_bible or {},
            "character_memory":character_memory or {}, "continuity_lock":True}
def recall(context, key):
    return context.get(key)
