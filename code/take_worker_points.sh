#!/usr/bin/env bash
# Take point files from worker branches BY NAME. Never merge a worker branch:
# a worker's checkout can carry anything else it touched, and the only thing
# wanted from it is the measurement.
set -uo pipefail
cd "$(dirname "$0")/.."
took=0
for b in $(git ls-remote --heads origin 2>/dev/null | awk '{print $2}' |
           sed 's|refs/heads/||' | grep '^worker-'); do
    git fetch -q origin "$b" 2>/dev/null || continue
    for f in $(git ls-tree -r --name-only FETCH_HEAD -- code/points 2>/dev/null); do
        [ -e "$f" ] && continue
        git checkout FETCH_HEAD -- "$f" 2>/dev/null && took=$((took+1)) &&
            echo "took $(basename "$f") from $b"
    done
done
echo "$took new point files taken"
