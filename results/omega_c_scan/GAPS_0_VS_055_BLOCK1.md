# THE GAPS TABLE AT omega_c = 0 AGAINST omega_c = 0.055, 23 September

Block 1 of each, two classes, JOINT, the same declared vector, the same code.
The only difference is omega_c, so this is the held-parameter comparison the
experiment calls for -- unlike two joint runs allowed to converge, which each
refit b to 0.10502 and measure no reduction at all.

## THE AUTHOR'S STANDING CHECK: IS IT MATERIALLY DIFFERENT? NO.

Three of twenty-three rows move by more than two points, and one of them is b.

-------------------------------------------------------------------------------------
h1                   0.021587     0.0077568    0.004           93.9%  HELD (rate inside the band)  [scored on band [0.004,0.01], band gap +0.00000]
b_smi                not printed  1.953        7.3             73.2%  HELD
...full tables below...

## THE FIRST CLEAN READING OF THE REDUCTION

    b at omega_c = 0      0.124483
    b at omega_c = 0.055  0.109739
    fall                  11.8 per cent

Against the author's 18 per cent, 0.055 falls short, so the scan should be
weighted to 0.075 and above rather than 0.055 to 0.065. Block 1 rather than
converged, so provisional -- but it agrees with the 11 to 21 band from oc00
against oc055 and with the 12 per cent measured earlier.

## TWO ROWS THAT MISLEAD, AND THE SCRIPT THAT SHOWS THEM WRONG

code/paper/calibration_report.py, which the /gaps skill runs, reports theta at
184 per cent and homelessness at 94. code/gaps_table.py, which CLAUDE.md says
IS the table, reports theta at 7.7 per cent labelled [aggregate, not
mean-of-ratios] and h1 as HELD, inside its band [0.004, 0.01]. The 184 figure
is the mean-of-ratios mislead CLAUDE.md documents. The two scripts have
diverged and the skill points at the wrong one.

## omega_c = 0
```
gaps table   log: code/oc2c0/run.log   blocks complete: 1

parameter            value        model        data              gap  update moves it
-------------------------------------------------------------------------------------
h1                   0.021587     0.0077568    0.004           93.9%  HELD (rate inside the band)  [scored on band [0.004,0.01], band gap +0.00000]
b_smi                not printed  1.953        7.3             73.2%  HELD
pi_v                 not printed  0.076933     0.266           71.1%  HELD
emp_homeless         not printed  0.21763      0.46            52.7%  NO INSTRUMENT (follows h_1)
h2                   0.040674     0.6006       0.406           47.9%  LOWER
pi_eu                0.026783     0.060277     0.049           23.0%  HELD
beta                 0.94559      3.6427       3               21.4%  LOWER
b                    0.0049192    0.12448      0.10502         18.5%  RAISE
tau_u                4.682        0.20033      0.245           18.2%  LOWER
c_bar                0.083843     0.0049338    0.0042          17.5%  LOWER
find_if_addicted     not printed  0.24631      0.217           13.5%  LOWER
aleph                87.416       89.775       80              12.2%  LOWER
tau_ell              0.89353      0.20045      0.224           10.5%  HELD
mu_H                 0.66642      1.3533       1.4732           8.1%  LOWER
kappa_phi_d_level    not printed  0.6828       0.74             7.7%  HELD
theta                0.165        0.14773      0.16             7.7%  HELD  [aggregate, not mean-of-ratios]
sigma_y              2.0635       0.16287      0.172            5.3%  HELD
newborn_endowment    0.11099      0.25264      0.26             2.8%  LOWER
p_m                  not printed  0.048608     0.048312         0.6%  HELD
gamma                0.5356       0.26912      0.268            0.4%  HELD
kappa_find_smi       10.797       0.24956      0.25             0.2%  RAISE
addiction_onset_base not printed  0.41301      0.41348          0.1%  RAISE
omega_c              -            not printed  -                   -  no moment in this log
delta_d              0.24         not printed  -                   -  no moment in this log

direction is parsed from the Fortran update line, not remembered.
RAISE/LOWER is what the rule does to the PARAMETER at the current gap.
```

## omega_c = 0.055
```
gaps table   log: code/oc055_bounds/run.log   blocks complete: 1

parameter            value        model        data              gap  update moves it
-------------------------------------------------------------------------------------
h1                   0.021587     0.0077185    0.004           93.0%  HELD (rate inside the band)  [scored on band [0.004,0.01], band gap +0.00000]
b_smi                not printed  2.0317       7.3             72.2%  HELD
pi_v                 not printed  0.07708      0.266           71.0%  HELD
emp_homeless         not printed  0.22193      0.46            51.8%  NO INSTRUMENT (follows h_1)
h2                   0.040674     0.60578      0.406           49.2%  LOWER
pi_eu                0.026783     0.059538     0.049           21.5%  HELD
beta                 0.94653      3.5985       3               20.0%  LOWER
c_bar                0.08379      0.0049485    0.0042          17.8%  LOWER
tau_u                4.6969       0.20605      0.245           15.9%  LOWER
aleph                87.416       90.19        80              12.7%  LOWER
tau_ell              0.89353      0.20041      0.224           10.5%  HELD
kappa_phi_d_level    not printed  0.67259      0.74             9.1%  HELD
mu_H                 0.66642      1.3472       1.4732           8.6%  LOWER
theta                0.165        0.14851      0.16             7.2%  HELD  [aggregate, not mean-of-ratios]
sigma_y              2.0635       0.16294      0.172            5.3%  HELD
b                    0.0049192    0.10974      0.10502          4.5%  RAISE
find_if_addicted     4.8265       0.22387      0.217            3.2%  LOWER
kappa_find_smi       10.763       0.25237      0.25             0.9%  LOWER
gamma                0.5356       0.2701       0.268            0.8%  HELD
addiction_onset_base not printed  0.41614      0.41348          0.6%  LOWER
newborn_endowment    0.11182      0.25853      0.26             0.6%  LOWER
p_m                  not printed  0.048493     0.048296         0.4%  HELD
omega_c              -            not printed  -                   -  no moment in this log
delta_d              0.24         not printed  -                   -  no moment in this log

direction is parsed from the Fortran update line, not remembered.
RAISE/LOWER is what the rule does to the PARAMETER at the current gap.
```
