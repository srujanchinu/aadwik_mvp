def build_studio_state(project, production_state, qc_gate=False):
    return {"project":project,"production_state":production_state,
            "qc_gate":qc_gate,"sections":["story","assets","production","audio","editing","qc","publishing","analytics"]}
def validate_navigation(state):
    required={"story","assets","production","audio","editing","qc","publishing","analytics"}
    return required.issubset(set(state["sections"]))
