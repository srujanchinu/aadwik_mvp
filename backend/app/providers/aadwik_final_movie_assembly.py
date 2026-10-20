def assemble_final_movie(sequence, audio_package, timeline, qc_report):
    if not sequence.get("shot_count"):
        raise ValueError("sequence is empty")
    if not audio_package.get("shot_count"):
        raise ValueError("audio package is empty")
    if not timeline.get("clips"):
        raise ValueError("timeline is empty")
    if qc_report.get("publishing_gate") is not True:
        raise ValueError("publishing QC gate is not open")

    return {
        "schema": "aadwik-final-movie-1.0",
        "status": "ASSEMBLED",
        "shot_count": sequence["shot_count"],
        "audio_shots": audio_package["shot_count"],
        "timeline_clips": len(timeline["clips"]),
        "qc_gate": "OPEN",
        "export_ready": True,
    }
