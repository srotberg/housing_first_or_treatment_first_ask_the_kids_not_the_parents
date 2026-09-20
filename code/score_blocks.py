#!/usr/bin/env python3
"""score_blocks.py <run.log>

Scores a cold-start benchmark's block trace against n90's own, which
CALIBRATION_RECIPE.md section 3 records for blocks 2-7.

WHY THIS IS THE RIGHT CONTROL. The standing rule is that a no-op control is
scored at 1e-4 relative, never on equality -- but that rule is for one
compiler. This container has gfortran 13.3 against whatever the archive was
built with, and a cold start on top, so the per-block MOVES are the strongest
available check that the reconstructed seed is the same economy. They are
ratios, so the level does not have to match for the shape to.
"""
import re, sys

# CALIBRATION_RECIPE.md section 3, measured on n90.
N90 = {2:(+1.519e-01,+1.474e-01,-7.405e-02,+2.059e-01),
       3:(-4.710e-03,+3.818e-03,-2.385e-02,+8.497e-02),
       4:(-1.064e-02,-7.125e-03,-1.876e-02,+3.885e-02),
       5:(-1.213e-02,-7.596e-03,-4.824e-03,+1.859e-02),
       6:(-7.761e-03,-6.165e-03,-8.046e-03,+9.079e-03),
       7:(-1.660e-03,-8.973e-03,-4.982e-03,+4.442e-03)}
NAMES=("b","lambda_d","h_1","y")
TARGET=dict(b=0.081740, lambda_d=0.033625, h_1=0.0064583)

num=r"[-+0-9.EDed]+"
pat=re.compile(r"BLOCK MOVE\s+("+num+r")\s+against a rule of\s+("+num+
               r")\s+--\s+b\s+("+num+r")\s+lambda_d\s+("+num+
               r")\s+h_1\s+("+num+r")\s+y\s+("+num+r")")
f=lambda s: float(s.replace('D','E').replace('d','e'))

rows=[]
for line in open(sys.argv[1],encoding="utf-8",errors="surrogateescape"):
    m=pat.search(line)
    if m: rows.append(tuple(f(x) for x in m.groups()))
if not rows: sys.exit("no BLOCK MOVE lines yet")

print("blk  %-11s %-11s %-11s %-11s   move       n90 move   ratio"%NAMES)
for i,(mv,rule,b,d,h,y) in enumerate(rows, start=1):
    if i==1:
        print("  1  %.6f    %.6f    %.7f  %.6f   ARTEFACT (cold policies; recipe s.3)"%(b,d,h,y))
        continue
    pb,pd,ph,py = rows[i-2][2:]
    got=((b-pb)/pb,(d-pd)/pd,(h-ph)/ph,(y-py)/py)
    ref=N90.get(i)
    bind=NAMES[max(range(4),key=lambda k:abs(got[k]))]
    s="%3d  "%i+" ".join("%+.3e"%g for g in got)
    s+="   %.3e"%max(abs(g) for g in got)
    if ref: s+="  %.3e  %.2f"%(max(abs(r) for r in ref),
                               max(abs(g) for g in got)/max(abs(r) for r in ref))
    else:   s+="   --         --"
    print(s+"   binding=%s"%bind)

mv,rule,b,d,h,y = rows[-1]
print("\nlatest levels against the n90 benchmark of record:")
for k,v in (("b",b),("lambda_d",d),("h_1",h)):
    print("  %-9s %.6f   target %.6f   %+.2f%%"%(k,v,TARGET[k],100*(v-TARGET[k])/TARGET[k]))
print("  block move %.4e against a rule of %.1e"%(mv,rule))
