#!/bin/bash
# Section 3's numbers, tables and figures on the Arias (2014) survival fit (3 October)
cd "$(dirname "$0")"
export STYLIZED_WORKERS=${STYLIZED_WORKERS:-2}
{ echo "start $(date -u +%H:%M)"
  python3 stage_results.py 1; echo "RES1 RC $? $(date -u +%H:%M)"
  python3 stage_results.py 2; echo "RES2 RC $? $(date -u +%H:%M)"
  python3 stage_results.py tables; echo "TABLES RC $? $(date -u +%H:%M)"
  python3 stage_transition.py; echo "TRANS RC $? $(date -u +%H:%M)"
  echo "ARIAS RESULTS DONE $(date -u +%H:%M)"; } > /tmp/claude-0/arias_results.log 2>&1
