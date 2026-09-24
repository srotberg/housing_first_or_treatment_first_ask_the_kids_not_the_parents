# A WORKER THAT GOES IDLE LOSES ITS SOLVE; ONE THAT WATCHES KEEPS IT, 24 September 06:33

Measured tonight across two workers running the same kind of solve:

    Housing First reference   background watcher on its log + self check-in   epoch 1 for 3.5 h
    Treatment First           idle between check-ins                          epoch 8, $130 spent

A session that goes fully idle has its container reclaimed, and the solve with
it. Each relaunch then cost a restart AND a turn over a 350k-token history.
Brief every long-solve worker to keep a background watcher armed on its log for
the whole run, re-armed on expiry, and keep the brief lean so each wake is
cheap. The Treatment First run was moved to a fresh lean session
(session_016mEcrWxYuSsKpMQits6Rmo) using the pushed build_tf_rationed.sh and
remote_tf_rationed.sh; the old session is archived.

