from aadwik_production_orchestrator import create_job
from aadwik_movie_pipeline import run_movie_pipeline

def validate_series(series):
    episodes = series.get("episodes", [])
    if not series.get("series_id") or not episodes:
        return False, "series_id and episodes are required"
    for i, ep in enumerate(episodes, 1):
        if not ep.get("episode_id") or not ep.get("production_payload"):
            return False, f"episode {i} missing episode_id or production_payload"
    return True, None

def build_series_package(series):
    ok, err = validate_series(series)
    if not ok:
        raise ValueError(err)
    results = []
    for ep in series["episodes"]:
        job = create_job(ep["episode_id"], "series_episode", ep["production_payload"].get("scenes", []))
        results.append(run_movie_pipeline(job, ep["production_payload"]))
    return {
        "schema": "aadwik-series-production-1.0",
        "series_id": series["series_id"],
        "episode_count": len(results),
        "episodes": results,
        "series_ready": all(x["state"] == "READY_TO_PUBLISH" for x in results)
    }
