TRACKS={"little_kids":(2,4),"kids":(5,7),"big_kids":(8,10)}
def select_track(age):
    for name,(lo,hi) in TRACKS.items():
        if lo<=age<=hi: return name
    raise ValueError("age outside 2-10")
def build_kids_content(age, theme):
    return {"age":age,"track":select_track(age),"theme":theme,
            "formula":"Fun -> Emotion -> Adventure -> Natural Learning"}
