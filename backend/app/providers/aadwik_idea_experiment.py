def create_idea(title, genre, audience):
    return {"title":title,"genre":genre,"audience":audience,"status":"IDEA"}
def create_experiment(name, hypothesis, variants):
    return {"name":name,"hypothesis":hypothesis,"variants":variants,"status":"READY"}
