"""
HPP Model Simulation Engine with Reflective Boundaries.
Implements the Hardy-Pomeau-Pazzis(HPP) lattice gas automaton
with reflective boundary conditions.
"""

import numpy as np


class HPPGrid:
    """
    A 2D grid for HPP model simulation with reflective boundary conditions.
    Each cell can contain particles moving in 4 directions using bitwise storage.
    """
    
    # Direction constants using uppercase for constants
    RIGHT_DIRECTION = 1    # → (binary: 0001)
    UP_DIRECTION = 2       # ↑ (binary: 0010)
    LEFT_DIRECTION = 4     # ← (binary: 0100)
    DOWN_DIRECTION = 8     # ↓ (binary: 1000)

    def __init__(self, grid_size):
        """
        Initialize an N x N grid with all cells empty.
        
        Parameters:
        grid_size (int): Size of the grid (N x N cells)
        """
        self.size = grid_size
        # Create N x N grid filled with zeros (empty cells)
        self.grid_state = np.zeros((grid_size, grid_size), dtype=int)

    def add_particle(self, row_idx, col_idx, direction):
        """
        Add a particle with a specified direction to a cell.
        Uses bitwise OR to add direction without affecting existing particles.
        
        Parameters:
        row_idx (int): Row index (0 to size-1)
        col_idx (int): Column index (0 to size-1)
        direction (int): Direction flag (RIGHT_DIRECTION, UP_DIRECTION, etc.)
        """
        self.grid_state[row_idx][col_idx] |= direction

    def get_grid_state(self):
        """
        Return the current state of the grid.
        
        Returns:
        numpy.ndarray: N x N array representing particle positions and directions
        """
        return self.grid_state

    def _move_right(self, row_idx, col_idx, target_grid):
        """
        Move a right-moving particle. If at right edge, reflect back as left-moving.
        
        Parameters:
        row_idx (int): Current row position
        col_idx (int): Current column position  
        target_grid (numpy.ndarray): Target grid for the next timestep
        """
        if col_idx == self.size - 1:  # Particle at right edge
            target_grid[row_idx][col_idx] |= self.LEFT_DIRECTION
        else: 
            target_grid[row_idx][col_idx + 1] |= self.RIGHT_DIRECTION

    def _move_up(self, row_idx, col_idx, target_grid):
        """
        Move an up-moving particle. If at top edge, reflect back as down-moving.
        """
        if row_idx == 0:  # Particle at top edge
            target_grid[row_idx][col_idx] |= self.DOWN_DIRECTION
        else: 
            target_grid[row_idx - 1][col_idx] |= self.UP_DIRECTION

    def _move_left(self, row_idx, col_idx, target_grid):
        """
        Move a left-moving particle. If at left edge, reflect back as right-moving.
        """
        if col_idx == 0:  # Particle at left edge
            target_grid[row_idx][col_idx] |= self.RIGHT_DIRECTION
        else: 
            target_grid[row_idx][col_idx - 1] |= self.LEFT_DIRECTION

    def _move_down(self, row_idx, col_idx, target_grid):
        """
        Move a down-moving particle. If at bottom edge, reflect back as up-moving.
        """
        if row_idx == self.size - 1:  # Particle at bottom edge
            target_grid[row_idx][col_idx] |= self.UP_DIRECTION
        else: 
            target_grid[row_idx + 1][col_idx] |= self.DOWN_DIRECTION

    def advance_time_step(self):
        """
        Advance the simulation by one timestep using two-phase update:
        1. Collision handling: Process particle interactions in current grid
        2. Propagation: Move particles to new positions in fresh grid
        
        Returns:
        HPPGrid: self for method chaining
        """
        # Create fresh grid for the next timestep
        next_grid = np.zeros((self.size, self.size), dtype=int) 
        
        # Process all cells for collisions and prepare movement
        for row_idx, grid_row in enumerate(self.grid_state): 
            for col_idx, cell_value in enumerate(grid_row):
                # Extract individual particle directions using bitwise AND
                has_right = cell_value & self.RIGHT_DIRECTION
                has_up = cell_value & self.UP_DIRECTION
                has_left = cell_value & self.LEFT_DIRECTION
                has_down = cell_value & self.DOWN_DIRECTION

                # Collision handling
                # Head-on collision: Right + Left → turns into Up + Down
                if has_right and has_left and not (has_up or has_down):
                    has_right, has_left = 0, 0
                    has_up, has_down = self.UP_DIRECTION, self.DOWN_DIRECTION
                
                # Head-on collision: Up + Down → turns into Right + Left  
                elif has_up and has_down and not (has_right or has_left):
                    has_up, has_down = 0, 0
                    has_right, has_left = self.RIGHT_DIRECTION, self.LEFT_DIRECTION

                # Propagation - Move particles to new positions
                if has_right:
                    self._move_right(row_idx, col_idx, next_grid)
                if has_up:
                    self._move_up(row_idx, col_idx, next_grid)
                if has_left:
                    self._move_left(row_idx, col_idx, next_grid)
                if has_down: 
                    self._move_down(row_idx, col_idx, next_grid) 

        # Update grid state
        self.grid_state = next_grid 
        return self
