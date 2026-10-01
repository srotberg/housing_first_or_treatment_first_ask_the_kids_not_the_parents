import sys, re, subprocess
log = open(sys.argv[1], errors="replace").read().splitlines()
rows = []; cur = {}
for l in log:
    s = l.strip()
    if s.startswith("probability_of_voucher="): cur["pv"] = float(s.split()[1])
    elif s.startswith("price_of_addictive_good="): cur["p"] = float(s.split()[1])
    elif s.startswith("CF MOMENTS distance="):
        f = s.split(); cur["b"] = float(f[5]); cur["ld"] = float(f[7]); cur["h"] = float(f[9])
    elif s.startswith("distance_drug_market="): cur["dd"] = float(s.split()[1])
    elif s.startswith("average_welfare_with_childhood="): cur["w"] = float(s.split()[1])
    elif s.startswith("distance_govt_budget="):
        cur["bg"] = float(s.split()[1]); rows.append(cur); cur = {}
B = dict(b=0.081255, ld=0.034611, h=0.0060789)
# PASSES_BASE="b,lambda_d,h_1" of another benchmark (stage C, the omega_c = 0.085 one); unset, as before
import os
if os.environ.get("PASSES_BASE"):
    B = dict(zip(("b", "ld", "h"), map(float, os.environ["PASSES_BASE"].split(","))))
print("pass  price    pi_V     b(chg)   SUD(chg)  h_1(chg)  drug gap  budget gap  welfare    CEV")
for i, r in enumerate(rows, 1):
    x = subprocess.run(["python3", sys.argv[2], str(r["w"])], capture_output=True, text=True, cwd="..").stdout
    m = re.search(r"CEV x = ([+-][0-9.]+)", x); cev = 100*float(m.group(1)) if m else float("nan")
    print(f"{i:>3}  {r['p']:.4f}  {r['pv']:.5f}  {100*(r['b']/B['b']-1):+6.1f}%  {100*(r['ld']/B['ld']-1):+6.1f}%  {100*(r['h']/B['h']-1):+6.1f}%  {r['dd']:.2e}  {r['bg']:.2e}   {r['w']:.4f}  {cev:+.2f}%")
