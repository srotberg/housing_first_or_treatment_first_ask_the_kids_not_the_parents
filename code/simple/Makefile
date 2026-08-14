# Simplified HF/TF model
FC      = gfortran
FFLAGS  = -O3 -march=native -funroll-loops -flto -fopenmp
COMMON  = params.f90 solve.f90 equilibrium.f90 calibrate.f90 mechanism.f90 experiment.f90
SRC     = $(COMMON) main.f90
TARGET  = hftf_simple

all: $(TARGET) calib mech exper check

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

# stricter build for debugging; -fcheck=all catches out-of-bounds indexing
debug: $(SRC)
	$(FC) -O0 -g -fbacktrace -fcheck=all $(SRC) -o $(TARGET)_debug

run: $(TARGET)
	OMP_NUM_THREADS=4 ./$(TARGET)

clean:
	rm -f *.mod $(TARGET) $(TARGET)_debug hftf_calib hftf_mech hftf_exper check_hours
.PHONY: all debug run clean calib mech
