from dataclasses import dataclass, field
from statistics import mean

@dataclass
class MetricSnapshot:
    platform:str
    views:int=0
    likes:int=0
    comments:int=0
    shares:int=0
    watch_time_seconds:float=0.0
    impressions:int=0

    @property
    def engagement_rate(self):
        base=self.impressions or self.views
        if base<=0: return 0.0
        return (self.likes+self.comments+self.shares)/base

    @property
    def avg_watch_time(self):
        return self.watch_time_seconds/self.views if self.views else 0.0

class AnalyticsEngine:
    def __init__(self): self.snapshots=[]
    def record(self,snapshot):
        self.snapshots.append(snapshot); return snapshot
    def platform_summary(self,platform):
        rows=[x for x in self.snapshots if x.platform==platform]
        return {
            "platform":platform,
            "count":len(rows),
            "views":sum(x.views for x in rows),
            "likes":sum(x.likes for x in rows),
            "comments":sum(x.comments for x in rows),
            "shares":sum(x.shares for x in rows),
            "engagement_rate":mean([x.engagement_rate for x in rows]) if rows else 0.0,
        }
