"""
User Interface for HPP Model with Reflective Boundaries.
Handles user input, initialization, and simulation control.
"""

from grid import HPPGrid
from animation import HPPVisualizer
import random


class HPPSimulation:
    """Main simulation controller and user interface."""
    
    def __init__(self):
        """Initialize the simulation with direction mapping."""
        self.direction_mapping = {
            'u': 2,  # Up ↑
            'd': 8,  # Down ↓
            'r': 1,  # Right →
            'l': 4   # Left ←
        }
        self.visualizer = HPPVisualizer()
        self.has_error = False

    def get_grid_size(self):
        """Get and validate grid size from user."""
        try:
            grid_size = int(input("Enter grid side length (e.g., 5, 10, 20): "))
            if grid_size < 3:
                print("Grid size must be at least 3")
                return None
            return grid_size
        except ValueError:
            print("Please enter a valid integer")
            return None
        except EOFError:
            print("\nNo input available. Using default grid size of 10.")
            return 10

    def initialize_random_particles(self, grid, grid_size):
        """Initialize particles with random positions and directions."""
        try:
            particle_count = int(input(f"\nEnter number of particles (1 to {grid_size*grid_size}): "))
            if particle_count < 1 or particle_count > grid_size * grid_size:
                print(f"Number of particles must be between 1 and {grid_size*grid_size}")
                return False

            print(f"Placing {particle_count} random particles...")
            for _ in range(particle_count):
                random_row = random.randint(0, grid_size - 1)
                random_col = random.randint(0, grid_size - 1)
                random_direction = random.choice([1, 2, 4, 8])
                grid.add_particle(random_row, random_col, random_direction)

            return True

        except ValueError:
            print("Please enter a valid number")
            return False
        except EOFError:
            print("\nNo input available. Using default particle count.")
            # Use a reasonable default (10% of grid capacity)
            default_count = max(1, (grid_size * grid_size) // 10)
            print(f"Placing {default_count} random particles...")
            for _ in range(default_count):
                random_row = random.randint(0, grid_size - 1)
                random_col = random.randint(0, grid_size - 1)
                random_direction = random.choice([1, 2, 4, 8])
                grid.add_particle(random_row, random_col, random_direction)
            return True

    def initialize_manual_particles(self, grid, grid_size):
        """Initialize particles based on user input."""
        print("\n" + "=" * 50)
        print("MANUAL PARTICLE PLACEMENT INSTRUCTIONS:")
        print("=" * 50)
        print(f"• Coordinates: 1 to {grid_size} (row and column)")
        print("• Directions: u (up), d (down), r (right), l (left)")
        print("• Multiple particles can be in same cell")
        print("• Example: '3 2 r' places right-moving particle at row 3, column 2")
        print("• Enter '-1' to finish input")
        print("=" * 50)

        particle_count = 0

        while True:
            try:
                user_input = input("Enter 'row col direction' or '-1' to finish: ").strip()

                if user_input == "-1":
                    if particle_count == 0:
                        print("Please add at least one particle")
                        continue
                    break

                # Parse input
                parts = user_input.split()
                if len(parts) != 3:
                    print("Please enter exactly 3 values: row, column, direction")
                    continue

                row_str, col_str, direction_str = parts
                row_idx = int(row_str) - 1  # Convert to 0-indexed
                col_idx = int(col_str) - 1  # Convert to 0-indexed

                # Validate coordinates
                if row_idx < 0 or row_idx >= grid_size or col_idx < 0 or col_idx >= grid_size:
                    print(f"Coordinates must be between 1 and {grid_size}")
                    continue

                # Validate and convert direction
                if direction_str not in self.direction_mapping:
                    print("Direction must be: u, d, r, or l")
                    continue

                direction_value = self.direction_mapping[direction_str]
                grid.add_particle(row_idx, col_idx, direction_value)
                particle_count += 1
                print(f"Added particle {particle_count}")

            except ValueError:
                print("Please enter valid numbers for row and column")
            except KeyboardInterrupt:
                print("\nInput cancelled")
                return False
            except EOFError:
                print("\nNo input available. Using default particle placement.")
                # Place a single particle in the center as default
                center = grid_size // 2
                grid.add_particle(center, center, 1)  # Right-moving particle
                print(f"Added 1 particle at center ({center+1}, {center+1}) moving right")
                return True

        return True

    def run_simulation(self):
        """Main simulation execution flow."""
        print("=" * 50)
        print("HPP MODEL SIMULATION WITH REFLECTIVE BOUNDARIES")
        print("=" * 50)
        print("Particles bounce off walls instead of wrapping around")
        print("=" * 50)
        
        # Get grid size
        grid_size = self.get_grid_size()
        if grid_size is None:
            return
        
        # Create grid
        simulation_grid = HPPGrid(grid_size)
        print(f"Created {grid_size}x{grid_size} grid with reflective boundaries")

        # Initialize visualization
        figure = self.visualizer.initialize_display()
        self.visualizer.update_frame(0, simulation_grid, grid_size, False, True)
        print("Empty grid displayed for reference")

        # Get initialization method
        print("\nHow would you like to initialize particles?")
        print("random (r) - Random particle placement")
        print("manually (m) - Manual particle placement")
        try:
            choice = input("Enter 'random' or 'manually' (r/m): ").lower().strip()
        except EOFError:
            print("\nNo input available. Using random placement.")
            choice = 'random'

        success = False
        if choice in ['random', 'r']:
            success = self.initialize_random_particles(simulation_grid, grid_size)
        elif choice in ['manually', 'm']:
            success = self.initialize_manual_particles(simulation_grid, grid_size)
        else:
            print("Invalid choice. Please enter 'random' or 'manually'")
            return

        if not success:
            return

        # Run simulation
        print("\nStarting simulation...")
        print("Close the animation window to continue")
        
        # Show animation
        self.visualizer.create_animation(figure, simulation_grid, True)
        
        # Offer to save GIF
        save_choice = input("\nSave animation as GIF? (y/n): ").lower().strip()
        if save_choice == 'y':
            self.visualizer.export_animation(figure, simulation_grid, True)
        
        print("Simulation completed!")


if __name__ == "__main__":
    simulator = HPPSimulation()
    simulator.run_simulation()
