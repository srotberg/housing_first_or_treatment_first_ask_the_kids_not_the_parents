import json, sys
g = lambda t: dict(zip(*json.load(open(f"{sys.argv[1]}/{t}.json"))["response"]["data"][:2]))
b = g("B25042"); r = g("B25020")
B = lambda i: float(b[f"B25042_{i:03d}E"]); Rr = lambda i: float(r[f"B25020_{i:03d}E"])
tot = B(1)
bed = [B(3) + B(10), B(4) + B(11), B(5) + B(12), B(6) + B(13), B(7) + B(14), B(8) + B(15)]
rooms = [Rr(3 + k) + Rr(13 + k) for k in range(9)]
pc = lambda xs: " / ".join(f"{100*x/tot:.1f}" for x in xs)
print("B25042 {0,1}/{2}/{3+}:", pc([bed[0] + bed[1], bed[2], sum(bed[3:])]))
print("B25042 {0}/{1}/{2+}:  ", pc([bed[0], bed[1], sum(bed[2:])]))
print("B25042 {0}/{1,2}/{3+}:", pc([bed[0], bed[1] + bed[2], sum(bed[3:])]))
print("B25020 rooms {1}/{2-5}/{6+}:", pc([rooms[0], sum(rooms[1:5]), sum(rooms[5:])]))
print("B25020 rooms {1-3}/{4-7}/{8+} (rung floors at 4 and 8):", pc([sum(rooms[:3]), sum(rooms[3:7]), sum(rooms[7:])]))
print("totals", tot, sum(bed), sum(rooms))
