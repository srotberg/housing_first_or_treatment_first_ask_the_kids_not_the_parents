# The archive benchmark's .dat set, compressed

The 90 `*baseline_benchmark.dat` files a transition reads as its initial
condition and its `old_results`, gzipped. 2.06 GB becomes 124 MB, about 17 to 1,
because they are fixed-format text. The largest single member is 35.1 MB, under
GitHub's per-file limit, which is why they are stored one gzip per file rather
than as one archive.

## Why this is committed when `code/trans_*/` is gitignored

Two reasons, and the second is the one that made it worth 124 MB.

**A fresh container could not get them at all.** `seeds/README.md` says a worker
"starts cold and pays a few extra blocks while the class-1 stock fills from
zero", because the distribution was too big to commit. Both T=60 sessions
re-solved a whole benchmark for this reason -- about four and a half hours each.
With these they do not have to.

**The two transition arms have to share ONE benchmark.** The author, 20
September: *"make both arms come off the same benchmark and code"*. The code was
never the problem -- grandfathered and not are one source and one compile-time
switch, asserted by value in the generated file. The benchmark was: each session
re-solved its own, in its own container, on a compiler neither original run used.
Each arm is internally consistent, so each CEV is sound, but the quantity the
paper wants is the DIFFERENCE between the arms, and at T=5 that was 1.6e-4
relative against a measured cross-container spread of 1.8e-2 on w_bot. A
difference two orders of magnitude smaller than the noise between the benchmarks
it is taken across is not a measurement.

These files are the archive's own benchmark, 09-19 16:31 -- not a re-solve of
it -- so an arm run against them is comparable with every result already in the
archive as well as with the other arm.

## The identity check before you trust a copy

    drug_supply_shifterbaseline_benchmark.dat    1.62001478993009917495

It is the only number a counterfactual takes from the benchmark's drug market,
and a restatement of V = 0.494427 through `1 = shifter*V^(1/eps_s)`. An x per
cent error there moves arm 3's price by `x/(1 + 0.685*|dlnV/dlnp|)`, so 2.2 to
7.3 times smaller across the measured elasticity range.

Two more worth reading, both exact in this set:

    govt_spending_on_housing_vouchers_2          0.69016419894283099
    median_income                                0.863112277979

## Unpacking

    cd <run directory>
    for f in code/seeds/benchmark_dat/*.gz; do gunzip -c "$f" > "$(basename "${f%.gz}")"; done

Nothing else is needed: `PARAM_HANDOVER.txt` comes from
`seeds/PARAM_HANDOVER_trans_bench.txt` and the price path from
`seeds/drug_price_path_seed_t*.txt`.
