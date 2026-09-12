#!/usr/bin/env python3
"""Emit each new every-100 gaps table, plus any freeze or failure line.

POLLS THE FILE RATHER THAN TAILING IT.  `tail --follow=name --retry` was tried
and it silently stopped emitting: sr_run.sh truncates the log with `> $LOG` on
every relaunch, and after a few of those the tail sat alive with its offset
past the new end of file and delivered nothing.  A live tail process is not
evidence that anything is being delivered, which is the same trap as a table
that has not moved looking like one converging slowly.

Re-reading the whole file each pass costs nothing at this size and cannot get
out of step with it: a truncation shows up as the iteration numbers going
backwards, which resets the seen set.
"""
import os, re, sys, time

LOG = sys.argv[1] if len(sys.argv) > 1 else 'sr_run_50k.log'
EVERY = int(sys.argv[2]) if len(sys.argv) > 2 else 100
seen, last_max, warned = set(), -1, set()

while True:
    try:
        txt = open(LOG, errors='replace').read()
    except FileNotFoundError:
        time.sleep(5); continue
    blocks = re.findall(r'  ITERATION (\S+)\n(.*?)(?=\n  ITERATION |\Z)', txt, re.S)
    nums = [int(n) for n, _ in blocks if n.isdigit()]
    if nums and max(nums) < last_max:          # the log was truncated: new run
        seen, warned = set(), set()
        print('*** log truncated -- a new run has started', flush=True)
    if nums:
        last_max = max(nums)
    for n, body in blocks:
        if not n.isdigit():
            continue
        i = int(n)
        if i % EVERY or i in seen:
            continue
        seen.add(i)
        print(f'  ITERATION {i}\n{body.rstrip()}\n', flush=True)
    for line in txt.split('\n'):
        if re.search(r'FROZEN|STOPPING|every gap inside two|^FINAL|Traceback'
                     r'|MemoryError|Killed', line) and line not in warned:
            warned.add(line)
            print('*** ' + line.strip(), flush=True)
    time.sleep(15)
