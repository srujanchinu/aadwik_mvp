def check_component(name,available=True,details=""):
    return {"name":name,"available":bool(available),"details":details}

def run_health_checks(components):
    results=[check_component(**x) for x in components]
    return {
        "passed":all(x["available"] for x in results),
        "components":results,
        "failed":[x["name"] for x in results if not x["available"]],
    }
