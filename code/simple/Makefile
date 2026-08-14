# Simplified HF/TF model
FC      = gfortran
FFLAGS  = -O2 -fopenmp
SRC     = params.f90 solve.f90 main.f90
TARGET  = hftf_simple

$(TARGET): $(SRC)
	$(FC) $(FFLAGS) $(SRC) -o $(TARGET)

# stricter build for debugging; -fcheck=all catches out-of-bounds indexing
debug: $(SRC)
	$(FC) -O0 -g -fbacktrace -fcheck=all $(SRC) -o $(TARGET)_debug

run: $(TARGET)
	OMP_NUM_THREADS=4 ./$(TARGET)

clean:
	rm -f *.mod $(TARGET) $(TARGET)_debug
.PHONY: debug run clean
