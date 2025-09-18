## **Tasks**:
Simulate the HPP model. The model is defined in the following way:
- The world is a regular square grid in two dimensions
- Particles can move only horizontally or vertically
- Each site can be in one of $16 = 2^4$ states: For each of the four movement
 directions a particle can be present or not.


  0 : no particle at site
  
  1 : left moving particle
  
  2 : up moving particle
  
  3 : (left + up) moving particle
  
  ... and so on...
  
  14 : up+right+down moving particle
  
  15 : all four direction present

- The system is evolved in discrete time steps. Each time step consists of two phases:

  - **A scattering phase**:
  
    Every site that is occupied by exactly two particles, which move
    back-to-back, is replaced by a site where this back-to-back direction is rotated by $90°$.


  - **A flow phase**:

    Particles move by one lattice spacing each.

### Initial and Boundary Conditions:
In Practice we are restricted to a finite lattice of e.g. size $N × N$. One
reasonable choice of boundary conditions is the following: Every particle,
that during the flow phase would leave the grid, gets “reflected” back to the
site it came from, just with opposite movement direction.
As for the initial condition: A random occupation probability is a good
but boring choice. More interesting would be random, except for a small
region, where all sites are left empty.

### Parallelization:
The simplest way to parallelize the model with MPI is the following: Split
the grid into $Nproc$ equal stripes of size $Nl × N$, where $Nl = N/Nproc$.
You can choose $N$ such that it is divisible by the number of processes. The
scattering phase can be evaluated by each process alone, but for the flow
phase the states of the first/last row of the bottom/top neighbor-process
need to be known. Add two extra rows to the local grid (→ $(Nl + 2) × N)$.
These will be the outer boundaries where a copy of the neighbor’s rows is
kept. The internal rows are $1 . . . Nl$. Before every flow phase each process
has to
- Send row $1$ to the top neighbor.
- Send row $Nl$ to the bottom neighbor.
- Receive a row from the top neighbor and write it to row $0$ of your local
grid.
- Receive a row from the bottom neighbor and write it to row $Nl + 1$ of
your local grid.

### Hints
- Use C/C++ or python and MPI. Start with a first version without parallelization.
- To test your code, look at particularly simple initial conditions, e.g.

  – One particle somewhere, everything else empty

  – Two head-on moving particles
- Add functionality to export configurations and plot them with e.g.
Matlab.
