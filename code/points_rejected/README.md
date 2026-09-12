# Points that must never be scored

A point lands here when it is on a DIFFERENT MODEL from the one being
calibrated, or when it did not actually solve.  `next_batch.py` globs
`points/point_*.txt`, so moving a file here is what keeps it out of the archive
while keeping the evidence.

This is the same discipline as `points_pregrid/`, which is preserved and never
scored.

## point_13581cd552.txt -- 12 September

Produced by `resume.sh` after the container was reclaimed at about 18:03 and
killed run 792f1b26ae at twenty-six loops.  resume.sh read its base from
RESTART_VECTOR.txt, which was stale, and the scrape only overwrites CALIBRATED
parameters, so three structural ones came through wrong:

    kappa_phi_d_level          8      should be 3.0
    bottom_productivity_level  0      should be 0.0905
    weight_on_child            0.1009 should be 0.09 (omega_c is pinned)
    merge_from_node            2      should be 1

It also reports "solved in 0 min" because it was stopped after three seconds,
so it is not a solution of anything.  resume.sh is fixed in the same commit.
