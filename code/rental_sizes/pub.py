import json, sys
for t, n in [("B25020", 21), ("B25042", 15)]:
    d = json.load(open(f"{sys.argv[1]}/{t}.json"))["response"]["data"]
    row = dict(zip(d[0], d[1]))
    print(t, [(f"{t}_{i:03d}E", row.get(f"{t}_{i:03d}E")) for i in range(1, n + 1)])
