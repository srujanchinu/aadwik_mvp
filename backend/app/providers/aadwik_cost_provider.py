PROVIDERS=("blender_local","external_ai_video","external_tts","external_music")
def estimate_cost(provider, units):
    rates={"blender_local":0.0,"external_ai_video":1.0,"external_tts":0.2,"external_music":0.3}
    if provider not in rates: raise ValueError("unknown provider")
    return round(rates[provider]*units,2)
def choose_provider(preferred, budget, units):
    cost=estimate_cost(preferred,units)
    if cost<=budget:return {"provider":preferred,"cost":cost,"within_budget":True}
    return {"provider":"blender_local","cost":0.0,"within_budget":True,"fallback":True}
