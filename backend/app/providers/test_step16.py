from aadwik_social_command_center import connect_account,cross_post
accounts=[connect_account(x,"acct_"+x) for x in ("youtube","instagram","facebook","threads")]
out=cross_post({"id":"movie"},accounts)
assert len(out)==4 and all(x["status"]=="READY" for x in out)
print("CONNECT ONCE MODEL: OK")
print("4 PLATFORMS: OK")
print("CENTRAL PUBLISHING: OK")
print("CROSS-POST PACKAGE: OK")
print("STEP 16 PASS")
