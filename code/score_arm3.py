#!/usr/bin/env python3
"""score_arm3.py <run.log>   Arm 3 against results/arm3_convergence/CONVERGED.md.

The acceptance test is NOT proximity at any one block. CONVERGED.md set it
before its own run: the movement must DECAY MONOTONICALLY into the stop and b
must land inside the measured cycle band [0.04492, 0.04732]. A converged flag
on a single block is not evidence -- the two earlier arm 3 runs both reported
CONVERGED and were the peak and the trough of one oscillation.
"""
import re,sys
T=dict(b=0.045287,lambda_d=0.018460,h_1=0.006542,pi_v=0.076347,price=0.833490)
BAND=(0.04492,0.04732)
num=r"[-+0-9.EDed]+"
f=lambda s: float(s.replace('D','E').replace('d','e'))
t=open(sys.argv[1],encoding="utf-8",errors="surrogateescape").read()
rows=[tuple(f(x) for x in m) for m in re.findall(
    r"CF MOMENTS distance=\s*("+num+r")\s+b=\s*("+num+r")\s+lambda_d=\s*("+num+
    r")\s+h_1=\s*("+num+r")",t)]
if not rows: sys.exit("no CF MOMENTS lines yet")
print("blk  CFdist      b          lambda_d   h_1         |db|       note")
for i,(d,b,l,h) in enumerate(rows,1):
    db="   --     " if i==1 else "%.3e"%abs(b-rows[i-2][1])
    note="cold value function block, outside the cycle" if i==1 else ""
    print("%3d  %.3e  %.6f  %.6f  %.7f  %s  %s"%(i,d,b,l,h,db,note))
d,b,l,h=rows[-1]
print("\nagainst CONVERGED.md:")
for k,v in (("b",b),("lambda_d",l),("h_1",h)):
    print("  %-9s %.6f   target %.6f   %+.2f%%"%(k,v,T[k],100*(v-T[k])/T[k]))
print("  b inside the measured cycle band [%.5f, %.5f]: %s"%(
    BAND[0],BAND[1],"YES" if BAND[0]<=b<=BAND[1] else "NO"))
print("  CF moments %.4e against the live rule 5e-4: %s"%(d,"ok" if d<=5e-4 else "NOT YET"))
if len(rows)>3:
    dbs=[abs(rows[i][1]-rows[i-1][1]) for i in range(1,len(rows))]
    mono=all(dbs[i+1]<dbs[i] for i in range(len(dbs)-3,len(dbs)-1)) if len(dbs)>=3 else False
    print("  |db| last three: %s   monotone decay: %s"%(
        " ".join("%.3e"%x for x in dbs[-3:]),"YES" if mono else "not yet"))
