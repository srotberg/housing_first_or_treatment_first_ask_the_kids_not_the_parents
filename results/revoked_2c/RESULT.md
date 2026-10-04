# The households whose voucher Treatment First revokes: SUD and mortality, short run, fixed prices

DRAFT, 4 October 21:20 UTC: the Treatment First path is done; the Housing First counterfactual path is running again
(the container restarted at about 21:00 and killed its first attempt). Tables and the headline follow when it lands.

Design and code: `code/revoked_2c/README.md`. Guards so far: `guard_T3_pair.txt` (all PASS).

## A bug found on the way: the model's forward kernel has a data race

The first T = 3 tracking run disagreed with the model's own distribution step by 7e-6 in one cell (5e-5 of the
largest cell), and two runs of the SAME plain binary on two threads disagreed with each other (b at t = 1:
0.056421324900 against 0.056421298660; lambda_d 0.038139160889 against 0.038139143152; h_1 identical). On one thread
the plain and tracking builds agree bit for bit on all 48 aggregate lines and the shadow kernel reproduces the model's
step to 0.0. So the model's parallel distribution loop is not deterministic. The likely culprit: in
`converge_to_stationary_equilibrium`, `is_addicted_1` is in the `shared` clause of the `!$omp parallel do`, and every
iteration writes `is_addicted_1=0` and then `=1` for a disorder state, so a thread can read another's transient 0 and
push a disordered household with the clean survival and transition rows. The comment there calls it benign because
the final value depends only on the outer index; the transient is what is not benign. It touches only disorder states,
which is what the data show (b and lambda_d move, h_1 does not). Size: about 1e-6 relative in one step on two threads.
Not fixed here (the brief: no equation or model code changes); every arm and transition in the repository carries it.
