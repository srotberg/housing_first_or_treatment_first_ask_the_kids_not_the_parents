---
description: Full gap table for every internally calibrated parameter
allowed-tools: Bash(cd:*), Bash(ls:*), Bash(python3:*), Bash(date:*), Bash(grep:*), Bash(tail:*)
---

Show the author the FULL gap table for the quantitative model: every parameter
the model calibrates internally, one row each, with its value, the moment it is
bracketed on, the model's value of that moment, the target, and the gap.

Run it against the newest live log — `supervisor_run.log` while the joint loop
is running, `sweep_b_run.log` during a b sweep:

```
\
LOG=$(ls -t code/supervisor_run.log code/sweep_b_run.log 2>/dev/null | head -1) && \
echo "reading $LOG" && python3 code/paper/calibration_report.py "$LOG"
```

Then report it, following these rules:

- **Every internally calibrated parameter gets a row.** Do not truncate to the
  worst few and do not report only the median gap: the author has asked for the
  whole table more than once and the median hides exactly the parameter that is
  stuck.
- **Nothing fixed or held gets a row.** The report already drops a parameter
  whose adjuster is zero and one whose `include_` flag is off. If a row survives
  that you believe is not actually being calibrated, say so rather than
  deleting it silently.
- **A row with `no scalar moment` is calibrated, not held.** Keep it, and say
  that its moment is not a single number rather than leaving the reader to
  guess from the dashes.
- **Say which log and how fresh it is.** A table read off a stale log is worse
  than no table. Give the log's name and the last loop it contains, and if the
  run is at a corner — participation at zero or near one, homelessness at zero —
  say so at the top, because at a corner the moments are not measuring anything
  and the ranking is meaningless.
- **Gaps are relative, in per cent, never the Fortran's absolute distances.**
- Do not read a rising income of drug users as a fault: Table 7 puts it at 0.74
  of average in the data against 0.41 in the old benchmark, so a rise toward
  0.74 is the model improving. Only a ratio above one is a problem.
