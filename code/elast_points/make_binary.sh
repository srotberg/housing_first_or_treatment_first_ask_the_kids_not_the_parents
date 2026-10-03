#!/bin/bash
# make_binary.sh <out dir> <points>  -- the 2 October elasticity binary with any list of price steps.
#
# The author, 2 October, on the five steps 1, 5, 10, 20 and 50 per cent: "can you try every single
# point betweeen -50 and +50 and average that for both? should be quick". The measurement that
# produced the paper's numbers (code/ELASTICITY_RESULT_2C.txt, accepted in
# ELASTICITY_RESULT_2C.accepted.md) is rebuilt EXACTLY -- the source at d62835db (md5 c6c28c6a, the
# one it was built from), the two numerics lines of build_bench_tdm_childsplit.sh (md5 dc6e5216),
# the diff it records (md5 0e5f08c4) -- and only its list of six multipliers is replaced.
# <points> is a comma-separated list of percent changes, e.g. -50,-40,-30,1,11,21; zero is refused.
# Each md5 is checked; a mismatch stops the build.
set -e
OUT=$1; PTS=$2
[ -n "$OUT" ] && [ -n "$PTS" ] || { echo "usage: $0 <out dir> <points>"; exit 1; }
CODE=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$OUT"
md5() { md5sum "$1" | cut -c1-8; }
# A CLOUD CLONE IS SHALLOW (fifty commits) and d62835db is hundreds back: both grid workers of 03 Oct
# 02:05 and 02:20 stopped on 'invalid object name'. Fetch it by its full hash, else deepen, and say which.
SHA=d62835dbe73e35cd32e8fc271dfd9e41846e64e9
R="$CODE/.."
if ! git -C "$R" cat-file -e "$SHA^{commit}" 2>/dev/null; then
    echo "make_binary: $SHA not in the clone (shallow: $(git -C "$R" rev-parse --is-shallow-repository)), fetching"
    git -C "$R" fetch -q --depth=1 origin "$SHA" 2>&1 || git -C "$R" fetch -q --unshallow origin 2>&1 || true
    git -C "$R" cat-file -e "$SHA^{commit}" 2>/dev/null || { echo "REFUSING: $SHA still unreachable"; exit 1; }
fi
git -C "$R" show "$SHA:code/housing_first_or_treatment_first_SR_v1.f90" > "$OUT/src.f90"
[ "$(md5 "$OUT/src.f90")" = c6c28c6a ] || { echo "REFUSING: source md5 $(md5 "$OUT/src.f90")"; exit 1; }
ln_of() { n=$(grep -n -F -x -- "$1" "$OUT/src.f90" | cut -d: -f1); [ "$(echo "$n" | wc -w)" = 1 ] || { echo "REFUSING: anchor not unique: $1"; exit 1; }; echo $n; }
BL=$(ln_of "                    stopping_rule_stationary_distribution=6*10.d0**(-4)")
WL=$(ln_of "        do while (distance_distribution>stopping_rule_stationary_distribution)")
sed -e "${BL}s/6\*10.d0\*\*(-4)/5*10.d0**(-5)/" \
    -e "${WL}s/do while (distance_distribution>stopping_rule_stationary_distribution)/do while ((distance_distribution>stopping_rule_stationary_distribution) .OR. (loop_count_dist<70))/" \
    "$OUT/src.f90" > "$OUT/same.f90"
[ "$(md5 "$OUT/same.f90")" = dc6e5216 ] || { echo "REFUSING: same.f90 md5 $(md5 "$OUT/same.f90")"; exit 1; }
# the recorded diff: from the first hunk header after "THE DIFF APPLIED" to the end of the file
awk 'f==0 && /THE DIFF APPLIED/ {f=1; next} f==1 && /^[0-9]+(,[0-9]+)?[acd][0-9]+(,[0-9]+)?$/ {f=2} f==2' \
    "$CODE/ELASTICITY_RESULT_2C.txt" > "$OUT/elast.diff"
patch -s -o "$OUT/patch.f90" "$OUT/same.f90" "$OUT/elast.diff"
[ "$(md5 "$OUT/patch.f90")" = 0e5f08c4 ] || { echo "REFUSING: patch.f90 md5 $(md5 "$OUT/patch.f90")"; exit 1; }
# the list: multipliers 1+p/100, NP of them
python3 - "$OUT/patch.f90" "$OUT/points.f90" "$PTS" <<'PY'
import sys
src, dst, pts = sys.argv[1], sys.argv[2], [float(x) for x in sys.argv[3].split(',')]
assert pts and all(p != 0 and -100 < p for p in pts), pts
s = open(src).read()
n = len(pts)
mult = ','.join('%.4fd0' % (1 + p / 100) for p in pts)
def rep(o, w):
    global s
    assert s.count(o) == 1, o
    s = s.replace(o, w)
rep('real(8), dimension(6) :: ems_mult,ems_part,ems_user,ems_addict',
    'real(8), dimension(%d) :: ems_mult,ems_part,ems_user,ems_addict' % n)
rep('ems_mult=(/1.01d0,1.02d0,1.05d0,1.10d0,1.20d0,1.50d0/)', 'ems_mult=(/' + mult + '/)')
rep('do ems_k=1,6', 'do ems_k=1,%d' % n)
assert s.count('sum(ems_part)/6.d0') == 1 and s.count('sum(ems_user)/6.d0') == 1 and s.count('sum(ems_addict)/6.d0') == 1
s = s.replace('/6.d0', '/%d.d0' % n)
assert len(max(s.split('\n'), key=len)) < 10000
open(dst, 'w').write(s)
print('points', n, pts)
PY
cd "$OUT"
gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium points.f90 -o hftf_elast 2> build.err
echo "built $OUT/hftf_elast, $(grep -c Error build.err) errors, md5 $(md5 hftf_elast)"
