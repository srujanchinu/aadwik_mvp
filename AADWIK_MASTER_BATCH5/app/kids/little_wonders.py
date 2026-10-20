AGE_TRACKS = {
    "2-4": {
        "name":"Little Kids",
        "formats":["rhymes","movement","simple stories","ABC","colors","shapes","numbers"],
        "formula":["Fun","Emotion","Natural Learning"],
    },
    "5-7": {
        "name":"Adventure Kids",
        "formats":["adventure","fantasy","dinosaurs","animals","space","comedy","simple mysteries"],
        "formula":["Fun","Emotion","Adventure","Natural Learning"],
    },
    "8-10": {
        "name":"Big Kids",
        "formats":["detective","mystery","robots","technology","sci-fi","treasure hunts","fantasy"],
        "formula":["Fun","Emotion","Adventure","Natural Learning"],
    },
}

def get_age_track(age):
    age=int(age)
    if 2 <= age <= 4: return AGE_TRACKS["2-4"]
    if 5 <= age <= 7: return AGE_TRACKS["5-7"]
    if 8 <= age <= 10: return AGE_TRACKS["8-10"]
    raise ValueError("Little Wonders supports ages 2-10.")

def build_kids_content_plan(age, topic, story_first=True):
    track=get_age_track(age)
    return {
        "age":int(age),
        "track":track["name"],
        "topic":topic,
        "story_first":bool(story_first),
        "learning_style":"natural_in_story",
        "formats":track["formats"],
        "formula":track["formula"],
    }
