"""Extract occupied housing units from the 2023 ACS 1-year PUMS US housing files."""
import sys
import pandas as pd

src_dir, out = sys.argv[1], sys.argv[2]
cols = ["SERIALNO", "STATE", "PUMA", "WGTP", "NP", "TYPEHUGQ", "BDSP", "RMSP", "BLD",
        "YRBLT", "TEN", "GRNTP", "RNTP", "VALP", "SMOCP", "HHLDRAGEP", "NOC", "HUPAOC",
        "HUPAC", "HHT", "HHT2", "HINCP", "ADJINC", "ADJHSG", "R18", "VACS"]
parts = []
for f in ["psam_husa.csv", "psam_husb.csv"]:
    for ch in pd.read_csv(f"{src_dir}/{f}", usecols=cols, chunksize=500_000, dtype={"PUMA": str, "STATE": str, "SERIALNO": str}):
        ch = ch[(ch.TYPEHUGQ == 1) & (ch.NP > 0)]
        parts.append(ch)
df = pd.concat(parts, ignore_index=True)
df.to_pickle(out)
print(len(df), df.WGTP.sum())
