PLATFORMS=("facebook","instagram","threads","youtube")
def connect_account(platform, account_id, capabilities=None):
    if platform not in PLATFORMS: raise ValueError("unsupported platform")
    return {"platform":platform,"account_id":account_id,"connected":True,
            "capabilities":capabilities or ["publish","schedule","analytics"]}
def cross_post(package, accounts):
    return [{"platform":a["platform"],"account_id":a["account_id"],"status":"READY"} for a in accounts if a.get("connected")]
