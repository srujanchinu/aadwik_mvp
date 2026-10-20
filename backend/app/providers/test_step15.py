from aadwik_publishing_engine import build_publication
p=build_publication({"qc_gate":"OPEN"},"youtube","acct_demo")
assert p["status"]=="READY"
print("PUBLISHING ENGINE: OK")
print("QC -> PUBLISHING: CONNECTED")
print("PLATFORM PACKAGE: OK")
print("STEP 15 PASS")
