# Simplified HF/TF model
FC      = gfortran
FFLAGS  = -O2 -fopenmp
COMMON  = params.f90 solve.f90 equilibrium.f90 calibrate.f90
SRC     = $(COMMON) main.f90
TARGET  = hftf_simple

all: $(TARGET) calib

$(TARGET): $(SRC)
	$(FC) $(FFLAGS) $(SRC) -o $(TARGET)

calib: $(COMMON) calib_main.f90
	$(FC) $(FFLAGS) $(COMMON) calib_main.f90 -o hftf_calib

# stricter build for debugging; -fcheck=all catches out-of-bounds indexing
debug: $(SRC)
	$(FC) -O0 -g -fbacktrace -fcheck=all $(SRC) -o $(TARGET)_debug

run: $(TARGET)
	OMP_NUM_THREADS=4 ./$(TARGET)

clean:
	rm -f *.mod $(TARGET) $(TARGET)_debug hftf_calib
.PHONY: all debug run clean calib
