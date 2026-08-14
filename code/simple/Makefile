# Simplified HF/TF model
FC      = gfortran
FFLAGS  = -O3 -march=native -funroll-loops -flto -fopenmp
COMMON  = params.f90 solve.f90 equilibrium.f90 calibrate.f90 mechanism.f90 experiment.f90 fiscal.f90 transition.f90 welfare.f90 safetynet.f90
SRC     = $(COMMON) main.f90
TARGET  = hftf_simple

all: $(TARGET) calib mech exper check diag ext trans smoke net

$(TARGET): $(SRC)
	$(FC) $(FFLAGS) $(SRC) -o $(TARGET)

calib: $(COMMON) calib_main.f90
	$(FC) $(FFLAGS) $(COMMON) calib_main.f90 -o hftf_calib

mech: $(COMMON) mech_main.f90
	$(FC) $(FFLAGS) $(COMMON) mech_main.f90 -o hftf_mech

exper: $(COMMON) exp_main.f90
	$(FC) $(FFLAGS) $(COMMON) exp_main.f90 -o hftf_exper

check: $(COMMON) check_hours.f90
	$(FC) $(FFLAGS) $(COMMON) check_hours.f90 -o check_hours

diag: $(COMMON) diag_check.f90
	$(FC) $(FFLAGS) $(COMMON) diag_check.f90 -o diag_check

ext: $(COMMON) ext_main.f90
	$(FC) $(FFLAGS) $(COMMON) ext_main.f90 -o hftf_ext

trans: $(COMMON) trans_main.f90
	$(FC) $(FFLAGS) $(COMMON) trans_main.f90 -o hftf_trans

net: $(COMMON) net_main.f90
	$(FC) $(FFLAGS) $(COMMON) net_main.f90 -o hftf_net

# structural regression suite -- run this after ANY change to solve.f90
smoke: $(COMMON) smoke.f90
	$(FC) $(FFLAGS) $(COMMON) smoke.f90 -o hftf_smoke

# stricter build for debugging; -fcheck=all catches out-of-bounds indexing
debug: $(SRC)
	$(FC) -O0 -g -fbacktrace -fcheck=all $(SRC) -o $(TARGET)_debug

# GFORTRAN_UNBUFFERED_ALL is not optional for long runs: libgfortran buffers
# its own output and stdbuf cannot reach it, so a multi-hour calibration writes
# literally zero bytes until a buffer fills. Verified with /proc/<pid>/io.
run: $(TARGET)
	OMP_NUM_THREADS=4 GFORTRAN_UNBUFFERED_ALL=1 ./$(TARGET)

clean:
	rm -f *.mod $(TARGET) $(TARGET)_debug hftf_calib hftf_mech hftf_exper check_hours diag_check hftf_ext hftf_trans hftf_smoke hftf_net
.PHONY: all debug run clean calib mech exper check diag ext trans smoke
