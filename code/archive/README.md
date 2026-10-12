# code/archive

`run_files/` holds 575 files that sat loose in `code/` until 12 October: batch definitions, run outputs and logs from
the calibration of August and September (`batch_*.txt`, `ROUND*.txt`, `SCATTER_*.txt`, `evidence_*.log`, ...).
They were moved only after checking that no tracked script, Fortran source, JSON file or `.claude` hook names them,
either outright or by a file-name pattern; files a script still names (`benchmark_of_record.txt`,
`calibration_state.dat`, `B_SWEEP_GRID.txt`, ...) and the families an old script builds by pattern (`CORRECT_*`,
`RESTORE_*`, `batch_stage*`, `worker_*`) stayed in `code/`. Notes that mention one of these files by bare name now
find it here.
