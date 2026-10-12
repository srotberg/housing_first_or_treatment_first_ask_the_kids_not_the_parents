# `code/arms4.txt` — the vertices of simplex 4

One line per point, each line a complete `name=value` argument list for
`code/run_one_point.sh`. Line 1 is the simplex centre; lines 2 onward are the
one-parameter arms off it.

A worker runs its point with a single command and no parsing:

    bash code/run_one_point.sh $(sed -n '7p' code/arms4.txt)

The file exists because workers were asked to extract their own arm from
`code/simplex.py` and several of them could not: the container they landed in
had no numpy, so the import failed before it reached the vector. A flat file
read by `sed` has no dependencies at all.
