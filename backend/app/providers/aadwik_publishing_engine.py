SCHEMA="aadwik-publishing-1.0"
PLATFORMS=("youtube","facebook","instagram","threads")
def build_publication(movie, platform, account_id):
    if platform not in PLATFORMS: raise ValueError("unsupported platform")
    if movie.get("qc_gate") != "OPEN": raise ValueError("QC gate must be open")
    return {"schema":SCHEMA,"platform":platform,"account_id":account_id,"status":"READY","approved":True}
