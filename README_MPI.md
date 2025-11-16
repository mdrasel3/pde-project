# MPI HPP Model Simulation with Strong Scaling Analysis

This code runs a parallel Hardy-Pomeau-Pazzis (HPP) lattice gas automaton simulation and evaluates strong scaling using MPI. It distributes computation across multiple processes and provides performance benchmarking using runtime statistics.

## Prerequisites

- **Python 3.x** is required.
- Required packages (add to `requirements.txt`):
  - numpy
  - matplotlib
  - mpi4py
  - scipy
- You must have MPI installed on your system (such as MS-MPI, MPICH or OpenMPI). On Windows, use Microsoft MPI, or a compatible distribution.

Install packages:
```bash
pip install -r requirements.txt
```

## Installation & Setup
1. Ensure an MPI implementation (Microsoft MPI, MPICH, or OpenMPI) is installed.
2. Install the Python package dependencies above.
3. (Optional) Create and activate a virtual environment:
   - **Windows:**
     ```bat
     python -m venv venv
     venv\Scripts ctivate
     ```
   - **Linux/macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

## Running the Simulation
Run the code using mpiexec (or mpirun) with the desired number of processes:
```bash
mpiexec -np <N> python mpi_hpp_scaling.py
```
Where `<N>` is the number of MPI processes.

## Usage Instructions
- On start, enter grid size (must be divisible by nproc), number of time steps, and initial condition (`single`, `test`, `headon`, or `random`).
- The code will save performance results as CSV and grid snapshots as .mat, .csv, and PNG files periodically.
- Run with a single process (N=1) first to record the serial baseline time (stored in a .txt file). Strong scaling and parallel efficiency can then be measured across runs with multiple processes.

## Outputs
- Performance results CSV: total time, communication time, computation time, speedup, parallel efficiency.
- Grid snapshots: `.mat` (MATLAB), `.csv`, and `.png` files.
- Serial baseline time: stored as a `.txt` file for future runs (required for speedup calculation).

## Notes
- Make sure the grid size is divisible by the number of processes.
- Supported initial conditions (input): `single`, `test`, `headon`, `random`.
- Code is cross-platform but requires compatible MPI and Python packages.

