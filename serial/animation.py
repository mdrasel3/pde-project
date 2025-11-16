"""
Visualization system for HPP Model.
Handles drawing, animation, and GIF export for the simulation
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from functools import partial
import copy


class HPPVisualizer:
    """Visualization system for HPP model simulations."""
    
    def __init__(self):
        """Initialize the visualizer with arrow configurations."""
        # Arrow configuration for visual representation
        self.arrow_vectors = { 
            1: (1, 0),   # Right → (dx=1, dy=0)
            4: (-1, 0),  # Left ← (dx=-1, dy=0)
            2: (0, 1),   # Up ↑ (dx=0, dy=1) 
            8: (0, -1)   # Down ↓ (dx=0, dy=-1)
        }
        
        # Special markers for collision states
        self.collision_states = {
            5: (1, 4),   # Right + Left collision →←
            10: (2, 8)   # Up + Down collision ↑↓
        }
        
        # Combinations for cells with multiple particles
        self.multi_particle_states = {
            3: (1, 2),    # Right + Up →↑
            6: (2, 4),    # Up + Left ↑←
            9: (1, 8),    # Right + Down →↓
            12: (4, 8),   # Left + Down ←↓
            7: (1, 2, 4),  # Right + Up + Left →↑←
            11: (1, 2, 8), # Right + Up + Down →↑↓
            13: (1, 4, 8), # Right + Left + Down →←↓
            14: (2, 4, 8), # Up + Left + Down ↑←↓
            15: (1, 2, 4, 8) # All four directions →↑←↓
        }
        
        self.arrow_scale = 0.25  # Scaling factor for arrow length

    def update_frame(self, frame_number, grid, grid_size, is_animating, is_first_frame):
        """
        Update function for animation frames. Called for each frame of animation.
        
        Parameters:
        frame_number (int): Current frame number
        grid (HPPGrid): The grid object to animate
        grid_size (int): Grid size
        is_animating (bool): Whether to advance simulation or just draw
        is_first_frame (bool): Special handling for initial state
        """
        # Advance simulation if this is an animation (not just drawing)
        if is_animating and (frame_number >= 1 or not is_first_frame):
            grid.advance_time_step()
        
        # Clear the previous frame
        plt.cla()
        plt.axis('off')  # Hide axes for cleaner look
        
        # Draw all particles in the grid
        for row_index, grid_row in enumerate(grid.get_grid_state()):
            for col_index, cell_value in enumerate(grid_row):
                # Convert array coordinates to plot coordinates
                plot_x = col_index + 1
                plot_y = grid_size - row_index - 1 + 1
                
                # Draw based on cell content
                if cell_value in self.arrow_vectors:
                    self._draw_single_arrow(plot_x, plot_y, cell_value)
                elif cell_value in self.multi_particle_states:
                    self._draw_multiple_arrows(plot_x, plot_y, cell_value)
                elif cell_value in self.collision_states:
                    self._draw_collision_marker(plot_x, plot_y)
        
        self._draw_grid_border(grid_size)
        self._draw_grid_lines(grid_size)

    def _draw_single_arrow(self, x_position, y_position, direction):
        """Draw a single arrow for a cell with one particle."""
        dx, dy = self.arrow_vectors[direction]
        plt.arrow(x_position, y_position, 
                 self.arrow_scale * dx, self.arrow_scale * dy, 
                 head_width=0.1, color='white')

    def _draw_multiple_arrows(self, x_position, y_position, cell_value):
        """Draw multiple arrows for a cell with multiple particles."""
        for direction in self.multi_particle_states[cell_value]:
            dx, dy = self.arrow_vectors[direction]
            plt.arrow(x_position, y_position,
                     self.arrow_scale * dx, self.arrow_scale * dy,
                     head_width=0.1, color='white')

    def _draw_collision_marker(self, x_position, y_position):
        """Draw a red star marker for collision states."""
        plt.scatter(x_position, y_position, s=150, color='red', marker='*')

    def _draw_grid_border(self, grid_size):
        """Draw grid border and coordinate labels."""
        for i in range(grid_size + 2):
            for j in range(grid_size + 2):
                if i == 0 or j == 0 or i == grid_size + 1 or j == grid_size + 1:
                    plt.plot(i, grid_size + 2 - j - 1, 'ko')  # Border dots
                
                # Add coordinate labels
                if i == 0 and j != grid_size + 1 and j != 0:
                    plt.text(i, grid_size + 2 - j - 1, str(j), color='white')
                if j == 0 and i != grid_size + 1 and i != 0:
                    plt.text(i, grid_size + 2 - j - 1, str(i), color='white')

    def _draw_grid_lines(self, grid_size):
        """Draw grid lines between cells."""
        for y in range(grid_size + 1):
            plt.plot([x + 0.5 for x in range(grid_size + 1)], 
                    [y + 0.5 for _ in range(grid_size + 1)], color='yellow', linestyle='-')
        for x in range(grid_size + 1):
            plt.plot([x + 0.5 for _ in range(grid_size + 1)], 
                    [y + 0.5 for y in range(grid_size + 1)], color='yellow', linestyle='-')

    def create_animation(self, figure, grid, should_animate):
        """
        Display real-time animation of the simulation.
        
        Parameters:
        figure: matplotlib figure object
        grid (HPPGrid): Grid object to animate
        should_animate (bool): Whether to animate or show static state
        """
        plt.ioff()  # Turn off interactive mode for animation
        grid_copy = copy.deepcopy(grid)  # Work with copy to preserve original
        
        anim = animation.FuncAnimation(
            figure, 
            partial(self.update_frame, grid=grid_copy, grid_size=grid.size, 
                    is_animating=should_animate, is_first_frame=True), 
            frames=100, 
            interval=170  # milliseconds between frames
        )
        plt.show()

    def export_animation(self, figure, grid, should_animate):
        """
        Save animation as GIF file.
        
        Parameters:
        figure: matplotlib figure object  
        grid (HPPGrid): Grid object to animate
        should_animate (bool): Whether to animate or show static state
        """
        plt.ioff()
        grid_copy = copy.deepcopy(grid)
        
        anim = animation.FuncAnimation(
            figure,
            partial(self.update_frame, grid=grid_copy, grid_size=grid.size,
                    is_animating=should_animate, is_first_frame=True),
            frames=100,
            interval=170
        )
        
        # Save as GIF with 2 FPS for better observation
        writer = animation.PillowWriter(fps=2)
        anim.save('hpp_simulation.gif', writer=writer)
        plt.cla()  # Clear after saving
        print("Animation saved as 'hpp_simulation.gif'")

    def initialize_display(self):
        """
        Initialize the plot for particle input and visualization.
        
        Returns:
        figure: matplotlib figure object
        """
        figure, axes = plt.subplots(figsize=(8, 8))
        figure.patch.set_facecolor('black')
        axes.set_facecolor("black")
        plt.ion()  # Interactive mode for real-time updates
        figure.show()
        return figure
