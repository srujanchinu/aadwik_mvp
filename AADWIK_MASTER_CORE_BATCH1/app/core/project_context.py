from dataclasses import dataclass, field

@dataclass
class CharacterLock:
    character_id: str
    name: str
    age: str|int|None = None
    appearance: dict = field(default_factory=dict)
    clothing: dict = field(default_factory=dict)
    personality: list = field(default_factory=list)
    voice_profile: dict = field(default_factory=dict)
    identity_locked: bool = True

@dataclass
class WorldLock:
    world_id: str
    name: str
    environment: dict = field(default_factory=dict)
    visual_style: str = 'cinematic_stylized_3d'
    continuity_rules: list = field(default_factory=list)
    identity_locked: bool = True

@dataclass
class StoryBible:
    project_id: str
    title: str = ''
    premise: str = ''
    genre: str = ''
    age_group: str = 'All Ages'
    language: str = 'English'
    themes: list = field(default_factory=list)
    characters: list = field(default_factory=list)
    worlds: list = field(default_factory=list)
    props: list = field(default_factory=list)
    continuity_rules: list = field(default_factory=list)
    def locked_character_ids(self): return {c.character_id for c in self.characters if c.identity_locked}
    def locked_world_ids(self): return {w.world_id for w in self.worlds if w.identity_locked}

def build_story_bible(project_id, story):
    chars=[]
    for x in story.get('characters',[]) or []:
        if isinstance(x,str): chars.append(CharacterLock(x,x))
        else:
            cid=str(x.get('character_id') or x.get('id') or x.get('name'))
            chars.append(CharacterLock(cid,str(x.get('name') or cid),x.get('age'),x.get('appearance',{}) or {},x.get('clothing',{}) or {},x.get('personality',[]) or [],x.get('voice_profile',{}) or {},True))
    worlds=[]
    for x in story.get('worlds',[]) or story.get('locations',[]) or []:
        if isinstance(x,str): worlds.append(WorldLock(x,x))
        else:
            wid=str(x.get('world_id') or x.get('id') or x.get('name'))
            worlds.append(WorldLock(wid,str(x.get('name') or wid),x.get('environment',{}) or {}))
    return StoryBible(project_id,str(story.get('title','')),str(story.get('premise') or story.get('story') or story.get('prompt') or ''),str(story.get('genre','')),str(story.get('age_group','All Ages')),str(story.get('language','English')),list(story.get('themes',[]) or []),chars,worlds,list(story.get('props',[]) or []),list(story.get('continuity_rules',[]) or []))
