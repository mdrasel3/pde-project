# Author: Md Rasel
# Matriculation Number: ****710

"""
MPI-parallelized HPP Model with timing and strong scaling analysis.

"""
import os
import sys
import time
import numpy as np
from mpi4py import MPI

import matplotlib.pyplot as plt
from scipy.io import savemat


class ParallelHPPGrid:
    """MPI-parallelized HPP grid with timing instrumentation."""

    # Direction constants
    RIGHT_DIRECTION = 1  # → (binary: 0001)
    UP_DIRECTION = 2  # ↑ (binary: 0010)
    LEFT_DIRECTION = 4  # ← (binary: 0100)
    DOWN_DIRECTION = 8  # ↓ (binary: 1000)

    def __init__(self, global_size):
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()

        if global_size % self.size != 0:
            if self.rank == 0:
                print(
                    f"Error: Global size {global_size} must be divisible by {self.size} processes"
                )
            MPI.Finalize()
            sys.exit(1)

        self.global_size = global_size
        self.local_rows = global_size // self.size
        self.local_grid = np.zeros((self.local_rows + 2, global_size), dtype=int)

        # Neighbor setup
        self.top_neighbor = self.rank - 1 if self.rank > 0 else MPI.PROC_NULL
        self.bottom_neighbor = (
            self.rank + 1 if self.rank < self.size - 1 else MPI.PROC_NULL
        )

        # Timing variables
        self.time_computation = 0.0
        self.time_communication = 0.0
        self.time_total = 0.0

    def initialize_particles(self, ic_choice):
        """Initialize particles based on choice."""
        # Rank 0 builds full initilization
        full_grid = None
        if self.rank == 0:
            # Create full grid initialization
            full_grid = np.zeros((self.global_size, self.global_size), dtype=int)

            if ic_choice == "test":
                # Diagonal pattern
                for i in range(min(10, self.global_size)):
                    if i < self.global_size and i < self.global_size:
                        full_grid[i, i] = self.RIGHT_DIRECTION
            elif ic_choice == "random":
                # Random particles
                num_particles = self.global_size * self.global_size // 20
                for _ in range(num_particles):
                    row = np.random.randint(0, self.global_size)
                    col = np.random.randint(0, self.global_size)
                    direction = np.random.choice(
                        [
                            self.RIGHT_DIRECTION,
                            self.UP_DIRECTION,
                            self.LEFT_DIRECTION,
                            self.DOWN_DIRECTION,
                        ]
                    )
                    full_grid[row, col] |= direction
            elif ic_choice == "headon":
                # Head-on collision test
                mid = self.global_size // 2
                full_grid[mid, mid - 2] = self.RIGHT_DIRECTION
                full_grid[mid, mid + 2] = self.LEFT_DIRECTION
            elif ic_choice == "single":
                # One particle at the grid center, moving RIGHT
                mid = self.global_size // 2
                full_grid[mid, mid] = self.RIGHT_DIRECTION
            else:
                full_grid = None

        # Prepare send counts and displacements
        counts = [self.local_rows * self.global_size] * self.size
        displs = [r * self.local_rows * self.global_size for r in range(self.size)]

        # Allocate a flat local buffer on every rank
        local_flat = np.zeros(self.local_rows * self.global_size, dtype=int)

        # Scatter the full grid rows as flat array
        self.comm.Scatterv(
            [full_grid.flatten() if self.rank == 0 else None, counts, displs, MPI.LONG],
            local_flat,
            root=0,
        )

        # Reshape local_grid (excluding ghost rows)
        self.local_grid[1 : self.local_rows + 1, :] = local_flat.reshape(
            self.local_rows, self.global_size
        )

    def exchange_boundaries(self):
        """Exchange ghost rows with neighboring processes."""
        comm_start = time.time()

        requests = []

        # Send to top, receive from bottom
        if self.top_neighbor != MPI.PROC_NULL:
            req = self.comm.Isend(self.local_grid[1, :], dest=self.top_neighbor, tag=10)
            requests.append(req)

        if self.bottom_neighbor != MPI.PROC_NULL:
            req = self.comm.Irecv(
                self.local_grid[self.local_rows + 1, :],
                source=self.bottom_neighbor,
                tag=10,
            )
            requests.append(req)

        # Send to bottom, receive from top
        if self.bottom_neighbor != MPI.PROC_NULL:
            req = self.comm.Isend(
                self.local_grid[self.local_rows, :], dest=self.bottom_neighbor, tag=20
            )
            requests.append(req)

        if self.top_neighbor != MPI.PROC_NULL:
            req = self.comm.Irecv(
                self.local_grid[0, :], source=self.top_neighbor, tag=20
            )
            requests.append(req)

        MPI.Request.Waitall(requests)

        self.time_communication += time.time() - comm_start

    def advance_time_step(self):
        """Advance simulation by one timestep with boundary conditions."""
        comp_start = time.time()

        self.exchange_boundaries()

        new_local_grid = np.zeros((self.local_rows + 2, self.global_size), dtype=int)

        for local_row in range(1, self.local_rows + 1):
            for global_col in range(self.global_size):
                cell_value = self.local_grid[local_row, global_col]

                has_right = bool(cell_value & self.RIGHT_DIRECTION)
                has_up = bool(cell_value & self.UP_DIRECTION)
                has_left = bool(cell_value & self.LEFT_DIRECTION)
                has_down = bool(cell_value & self.DOWN_DIRECTION)

                # COLLISION HANDLING - HPP rules
                if has_right and has_left and not (has_up or has_down):
                    has_right, has_left = False, False
                    has_up, has_down = True, True
                elif has_up and has_down and not (has_right or has_left):
                    has_up, has_down = False, False
                    has_right, has_left = True, True

                # PROPAGATION with boundary conditions
                if has_right:
                    if global_col == self.global_size - 1:
                        new_local_grid[local_row, global_col] |= self.LEFT_DIRECTION
                    else:
                        new_local_grid[
                            local_row, global_col + 1
                        ] |= self.RIGHT_DIRECTION

                if has_left:
                    if global_col == 0:
                        new_local_grid[local_row, global_col] |= self.RIGHT_DIRECTION
                    else:
                        new_local_grid[local_row, global_col - 1] |= self.LEFT_DIRECTION

                if has_up:
                    # Only reflect at GLOBAL top boundary
                    if self.rank == 0 and local_row == 1:
                        new_local_grid[local_row, global_col] |= self.DOWN_DIRECTION
                    else:
                        new_local_grid[local_row - 1, global_col] |= self.UP_DIRECTION

                if has_down:
                    # Only reflect at GLOBAL bottom boundary
                    if self.rank == self.size - 1 and local_row == self.local_rows:
                        new_local_grid[local_row, global_col] |= self.UP_DIRECTION
                    else:
                        new_local_grid[local_row + 1, global_col] |= self.DOWN_DIRECTION

        self.local_grid = new_local_grid
        self.time_computation += time.time() - comp_start

    def count_particles(self):
        """Count total particles in simulation."""
        local_count = 0
        for local_row in range(1, self.local_rows + 1):
            for global_col in range(self.global_size):
                cell = self.local_grid[local_row, global_col]
                local_count += bin(cell).count("1")  # Count set bits

        total_count = self.comm.allreduce(local_count, op=MPI.SUM)
        return total_count if self.rank == 0 else None

    def save_configuration(self, timestep, format="mat"):
        """Save grid configuration to file."""

        # Prepare send counts and displacements
        counts = [self.local_rows * self.global_size] * self.size
        displs = [r * self.local_rows * self.global_size for r in range(self.size)]

        # Gather all local grids into a flat array on rank 0
        local_flat = self.local_grid[1 : self.local_rows + 1, :].flatten()

        # Prepare receive buffer on rank 0
        if self.rank == 0:
            full_flat = np.empty(self.global_size * self.global_size, dtype=int)
        else:
            full_flat = None

        self.comm.Barrier()

        # Timing communication for gathering
        comm_start = time.time()
        # Gather the data
        self.comm.Gatherv(local_flat, [full_flat, counts, displs, MPI.LONG], root=0)

        # Reshape and save on rank 0
        if self.rank == 0:
            full_grid = full_flat.reshape(self.global_size, self.global_size)

            # Save to file
            if format == "csv":
                np.savetxt(
                    f"config_{ic_choice}_t{timestep}.csv",
                    full_grid,
                    delimiter=",",
                    fmt="%d",
                )
            else:
                savemat(
                    f"config_{ic_choice}_t{timestep}.mat",
                    {
                        "grid": full_grid,
                        "timestep": timestep,
                        "global_size": self.global_size,
                    },
                )

            # Optional: Plot and save figure
            plt.figure(figsize=(8, 8))
            plt.imshow(full_grid, cmap="gray", interpolation="nearest")
            plt.axis("off")
            plt.title(f"HPP Configuration at Timestep {timestep}")
            plt.colorbar(label="Particle Directions (bitwise)")
            plt.savefig(f"{ic_choice}_t{timestep}.png", dpi=300, bbox_inches="tight")
            plt.close()


def run_scaling_benchmark(global_size, time_steps, ic_choice="test"):
    """Run simulation with comprehensive timing analysis."""
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Create grid
    grid = ParallelHPPGrid(global_size)

    # Initialize
    init_start = time.time()
    grid.initialize_particles(ic_choice)
    init_time = time.time() - init_start

    # Everyone must participate in the Reduce used by count_particles()
    initial_particles = grid.count_particles()

    # Main simulation with timing
    if rank == 0:
        print(
            f"Starting simulation: {global_size}x{global_size} grid, {time_steps} steps on {size} processes"
        )
        print(f"Initial particle count: {initial_particles}")
        print("=" * 70)

    # Synchronize all processes before timing
    comm.Barrier()

    total_start = time.time()

    # Safe intervals (avoid modulo-by-zero when time_steps is small)
    snapshot_interval = max(1, time_steps // 5)
    # report_interval   = max(1, time_steps // 10)

    # Run simulation
    for step in range(time_steps):
        step_start = time.time()
        grid.advance_time_step()

        # Optional: Save configurations periodically (~5 snapshots)
        if step % snapshot_interval == 0:
            grid.save_configuration(step, format="mat")

        # Everyone calls the collective; only rank 0 prints
        # if step % report_interval == 0:
        #    particles = grid.count_particles()
        #    if rank == 0:
        #        print(f"Step {step:4d}: {particles} particles")

    comm.Barrier()
    total_time = time.time() - total_start

    # Gather timing statistics
    all_comp_times = comm.gather(grid.time_computation, root=0)
    all_comm_times = comm.gather(grid.time_communication, root=0)

    # Compute final particle count collectively before root-only printing
    final_particles = grid.count_particles()
    if rank == 0:
        # Calculate statistics
        avg_comp = np.mean(all_comp_times)
        avg_comm = np.mean(all_comm_times)
        max_comp = np.max(all_comp_times)
        max_comm = np.max(all_comm_times)

        # Parallel efficiency metrics
        parallel_efficiency = None
        if size > 1:
            # Read serial time from file if available
            serial_time_file = f"serial_time_{global_size}.txt"
            if os.path.exists(serial_time_file):
                with open(serial_time_file, "r") as f:
                    serial_time = float(f.read().strip())
                speedup = serial_time / total_time
                parallel_efficiency = speedup / size
            else:
                print("Warning: Serial baseline time not found. Run with np=1 first.")

        # Save results
        results_file = (
            f"scaling_results_{global_size}x{global_size}_t{time_steps}_n{size}.csv"
        )
        file_exists = os.path.exists(results_file)

        with open(results_file, "a") as f:
            if not file_exists:
                f.write(
                    "nproc,total_time,avg_comp_time,avg_comm_time,max_comp_time,max_comm_time,parallel_efficiency\n"
                )
            f.write(
                f"{size},{total_time:.6f},{avg_comp:.6f},{avg_comm:.6f},{max_comp:.6f},{max_comm:.6f},{parallel_efficiency}\n"
            )

        # Save serial baseline
        if size == 1:
            with open(f"serial_time_{global_size}.txt", "w") as f:
                f.write(str(total_time))

        # Print results
        print("=" * 70)
        print(
            f"PERFORMANCE RESULTS (Grid: {global_size}x{global_size}, Steps: {time_steps})"
        )
        print("=" * 70)
        print(f"Number of processes: {size}")
        print(f"Total execution time: {total_time:.4f} seconds")
        print(f"Average computation time: {avg_comp:.4f} seconds")
        print(f"Average communication time: {avg_comm:.4f} seconds")
        print(f"Communication overhead: {100*avg_comm/total_time:.2f}%")
        if parallel_efficiency is not None:
            print(f"Parallel efficiency: {100*parallel_efficiency:.2f}%")
        print("=" * 70)
        print(f"Final particle count: {final_particles}")
        print(f"Results saved to: {results_file}")


if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        print("=" * 80)
        print("MPI HPP SIMULATION WITH STRONG SCALING ANALYSIS")
        print("=" * 80)
        print("Usage: mpirun -np <N> python mpi_hpp_scaling.py")
        print("=" * 80)

        # Get parameters
        global_size = int(input("Enter grid size (must be divisible by nproc): "))
        time_steps = int(input("Enter number of time steps: "))
        ic_choice = (
            input("Initial condition (single/test/headon/random): ").lower().strip()
        )

        if ic_choice not in ["single", "test", "random", "headon"]:
            print("Invalid choice. Using 'test' as default.")
            ic_choice = "test"
    else:
        global_size = 0
        time_steps = 0
        ic_choice = "test"

    # Broadcast parameters to all processes
    global_size = comm.bcast(global_size, root=0)
    time_steps = comm.bcast(time_steps, root=0)
    ic_choice = comm.bcast(ic_choice, root=0)

    # Run benchmark
    run_scaling_benchmark(global_size, time_steps, ic_choice)
