---
description: The author's gaps table -- 23 parameters, value, model, data, gap, direction
allowed-tools: Bash(cd:*), Bash(ls:*), Bash(python3:*), Bash(date:*), Bash(grep:*), Bash(tail:*), Bash(ps:*)
---

Show the author THE gaps table. They asked for this one specifically on 16
September and called it key:

> *"I want you to show me for each gaps table the targets for all of these:
> beta, sigma_y, theta, gamma, find_if_addicted, mu_H, pi_eu,
> addiction_onset_base, h1, newborn endowment, omega_c, tau_ell, c bar,
> kappa_phi_d_level, kappa_find_smi, pi_v, p_m, tau_u, aleph, b, delta_d, h2,
> emp_homeless. Can you automate it for me so this is the table you always show
> me? i want the parameter value, the model value, the data value, the gap, the
> direction of update at the current model and data gap"*

It is automated. Run it against the newest live log:

```
\
LOG=$(ls -t /tmp/claude-*/*/scratchpad/*/run.log code/supervisor_run.log 2>/dev/null | head -1) && \
echo "reading $LOG" && python3 code/gaps_table.py "$LOG"
```

`code/gaps_table.py` produces exactly the five columns asked for and parses the
UPDATE DIRECTION out of the Fortran rather than from memory.

## Rules for reporting it

- **Show all twenty-three rows.** Do not truncate to the worst few and do not
  report a median: the author has asked for the whole table repeatedly, and a
  median hides the parameter that is stuck.

- **Say which log and how many blocks it has.** A table off a stale log is
  worse than no table. If the run is at a corner -- participation at zero,
  homelessness at zero -- say so at the top, because at a corner the moments
  measure nothing and the ranking is meaningless.

- **Gaps are relative, in per cent**, never the Fortran's absolute distances.

- **A block count is not a loop count.** `loop_count` in the Fortran advances
  TWICE per moment block; it prints 2, 4, 6. Getting this wrong made a freeze
  fire at block 7 when it was set for 13.

## Three rows that are read wrong if taken at face value

- **theta** is reported on the AGGREGATE, sum spend over sum income, which is
  the author's standing instruction. The `MOMENT theta` row is a mass-weighted
  MEAN OF RATIOS that runs three to four times the aggregate: on 16 September it
  read 191 per cent off while the aggregate the author cares about was 8 per
  cent off. The script labels the row; keep the label when reporting.

- **emp_homeless** has NO INSTRUMENT. It moves only as a by-product of h_1, so
  it has no parameter and no direction, and its gap is not a failing
  instrument. Measured slope: emp_homeless rises as h_1 falls, about -22 per
  unit h_1 within a run.

- **A parameter that reads "not printed"** was gated that block -- the drug
  cooldown held it, or kappa's gate was shut. It is not a missing value and not
  a zero.

## Do not read these as faults

- A rising income of drug users. Table 7 puts it at 0.74 of average in the data
  against 0.41 in the old benchmark, so a rise toward 0.74 is the model
  improving. Only a ratio above one is a problem.

- An instrument whose direction looks backwards. Several are counterintuitive
  and MEASURED: raising `addiction_onset_base` LOWERS the disorder rate,
  because making use riskier deters people from using at all and the extensive
  margin beats the conversion margin. On 15 September that sign was very nearly
  "fixed"; the comment beside it records an earlier round that made exactly that
  mistake and spent nineteen loops paying for it. The script reads the direction
  out of the source for this reason -- trust it over memory, including mine.
