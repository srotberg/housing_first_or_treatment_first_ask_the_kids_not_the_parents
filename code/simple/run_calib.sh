#!/bin/bash
export GFORTRAN_UNBUFFERED_ALL=1 OMP_NUM_THREADS=4
./hftf_calib 8 >> calib_s1.log 2>&1
echo "=== hftf_calib exited with code $? at $(date) ===" >> calib_s1.log
