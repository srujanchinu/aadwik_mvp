def generate_insights(snapshots):
    if not snapshots:
        return {"insights":[],"recommendations":[]}
    total_views=sum(x.views for x in snapshots)
    avg_engagement=sum(x.engagement_rate for x in snapshots)/len(snapshots)
    best=max(snapshots,key=lambda x:x.views)
    return {
        "insights":[
            {"type":"performance","message":f"Highest-view snapshot is on {best.platform}.","views":best.views},
            {"type":"engagement","message":"Average engagement rate calculated from recorded snapshots.","rate":avg_engagement},
        ],
        "recommendations":[
            "Use performance data as guidance for future content decisions.",
            "Do not automatically rewrite or degrade story quality solely to chase views.",
        ],
        "total_views":total_views,
    }
