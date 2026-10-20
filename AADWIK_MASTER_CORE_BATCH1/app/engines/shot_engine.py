def plan_shots(scenes,shots_per_scene=2):
    if shots_per_scene<1: raise ValueError('shots_per_scene must be >= 1')
    out=[]; n=1
    for s in scenes:
        for i in range(shots_per_scene):
            out.append({'shot_id':f'shot_{n:04d}','scene_number':s.get('scene_number'),'shot_number':i+1,'framing':['wide','medium','close'][min(i,2)],'emotion':s.get('emotion',''),'characters':s.get('characters',[]),'locations':s.get('locations',[]),'props':s.get('props',[]),'continuity_locked':False,'production_status':'PLANNED'})
            n+=1
    return out
