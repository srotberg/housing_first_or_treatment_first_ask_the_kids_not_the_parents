# THE T = 60 TRANSITION IS STOPPED, 24 September 03:50

The author: *"maybe stop the transition simulation. i am going to run out of
token before it finishes"*. The transition session (session_01YQDuLa1YjVA3oZyht6YGQt)
was interrupted and told to kill its solves by pid, revert the killed .dat
files, push any unpushed scripts and a short note at
`results/transition/T60_STOPPED.md`, and go idle with nothing armed.

The T = 60 run itself never started. What stands from the work: the build-guard
fix (46bbe31c, assert switches by value), the memory sizing (about 10.5 GB at
T = 60 against a 13.36 GB cap), and the per-loop cost from T3_GROUNDWORK.md
(about 19 hours per path iteration at two threads, loop count unknown). Whether
a loop can restart from disk after a container rebuild was asked and is recorded
in the note if it was established. The counterfactual steady states carry on.

