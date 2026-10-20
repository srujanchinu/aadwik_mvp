def validate_av(video_duration,audio_tracks):
    issues=[]
    for name,start,duration in audio_tracks:
        if start<0 or duration<=0 or start+duration>video_duration+1e-6:
            issues.append(name)
    return {"valid":not issues,"issues":issues}
