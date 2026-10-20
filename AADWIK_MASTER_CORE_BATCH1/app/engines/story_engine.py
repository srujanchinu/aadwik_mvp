def understand_story(story,genre='',age_group='All Ages',language='English'):
    text=(story or '').strip()
    if not text: raise ValueError('Story cannot be empty.')
    return {'premise':text,'genre':genre or 'General','age_group':age_group,'language':language,'story_understanding':{'characters':[],'locations':[],'objects':[],'emotional_arc':[],'conflict':None,'resolution':None},'locked':False}

def breakdown_scenes(understanding,scene_count=5):
    if scene_count<1: raise ValueError('scene_count must be >= 1')
    templates=[('Setup','Establish the world, protagonist and situation.','Curiosity'),('Inciting Event','Introduce the event that changes direction.','Surprise'),('Challenge','Present an obstacle requiring action.','Tension'),('Emotional Turn','Give a believable emotional turning point.','Hope'),('Resolution','Resolve the central movement.','Joy')]
    out=[]
    for i in range(scene_count):
        t,d,e=templates[min(i,4)]
        out.append({'scene_number':i+1,'title':t,'description':d,'story_reference':understanding['premise'],'emotion':e,'status':'PLANNED','continuity_locked':False})
    return out
