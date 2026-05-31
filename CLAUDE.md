# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Installation
```bash
# Clone repository and navigate to project
git clone <https://github.com/mdrasel3/pde-project>
cd pde-project

# Create and activate virtual environment
# Windows:
python -m venv venv
venv\Scripts\activate
# Linux/macOS:
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r serial/requirements.txt
```

### Running the Simulation
```bash
# Run the HPP model simulation from the serial directory
cd serial
python main.py
```

### Testing Individual Components
While the project doesn't have formal unit tests, you can test components individually:
```bash
# Test grid functionality
python -c "
from grid import HPPGrid
grid = HPPGrid(5)
grid.add_particle(2, 2, 1)  # Add right-moving particle
print('Grid state:')
print(grid.get_grid_state())
"

# Test visualization components
python -c "
from animation import HPPVisualizer
viz = HPPVisualizer()
print('Visualizer initialized successfully')
"
```

## Project Architecture

### High-Level Structure
```
pde-project/
├── serial/                 # Main implementation directory
│   ├── main.py            # User interface and simulation controller
│   ├── grid.py           # HPP model physics engine
│   ├── animation.py      # Visualization and GIF export
│   ├── requirements.txt  # Python dependencies
│   └── output.gif        # Sample animation output
├── exmp_bitwise_operation.py  # Bitwise operations demonstration
└── README.md             # Project overview and usage instructions
```

### Core Components

1. **HPPGrid (grid.py)**: 
   - Implements the HPP lattice gas automaton with reflective boundary conditions
   - Uses bitwise operations to track particle directions (1=right, 2=up, 4=left, 8=down)
   - Two-phase update: collision handling followed by particle propagation
   - Reflective boundaries: particles bounce back with opposite direction when hitting edges

2. **HPPSimulation (main.py)**:
   - Handles user interaction and simulation workflow
   - Manages grid initialization (random or manual particle placement)
   - Controls simulation execution and visualization
   - Provides option to save animation as GIF

3. **HPPVisualizer (animation.py)**:
   - Creates real-time visualization using matplotlib
   - Draws particles as arrows indicating direction
   - Special markers for collision states (head-on collisions)
   - Ex animations as GIF files

### Key Algorithms
- **Collision Detection**: Head-on collisions (right+left or up+down) rotate directions by 90°
- **Movement Logic**: Particles move one lattice spacing per timestep with reflective boundaries
- **Bitwise Storage**: Efficient storage of multiple directions per cell using bit flags
- **Animation Framework**: matplotlib FuncAnimation for real-time visualization

### Data Flow
1. User specifies grid size and particle placement via main.py
2. HPPSimulation creates HPPGrid instance and initializes particles
3. Animation loop calls grid.advance_time_step() for each frame
4. HPPVisualizer renders current grid state
5. Process repeats until user closes window
6. Option to export animation as GIF

## Common Development Tasks

### Modifying Physics Rules
To change collision behavior or movement rules:
1. Edit `grid.py` in the `advance_time_step()` method
2. Modify collision handling logic (lines 116-125)
3. Adjust movement methods (_move_*) if changing boundary behavior

### Changing Visualization
To modify how the simulation appears:
1. Edit `animation.py` in the HPPVisualizer class
2. Adjust arrow vectors, colors, or marker styles
3. Modify frame rate or animation duration in create_animation/export_animation

### Adding New Features
To extend functionality:
1. For new physics: modify grid.py methods
2. For new UI options: update main.py input handling
3. For new visualizations: enhance animation.py drawing methods

## Dependencies
- Python 3.x
- numpy (for array operations)
- matplotlib (for visualization and animation)
- Pillow (for GIF export, via matplotlib)

All dependencies are listed in `serial/requirements.txt`.

## Notes for Future Development
- The simulation uses reflective boundaries (not periodic)
- Grid size must be ≥ 3 for meaningful behavior
- Particle directions are stored as bit flags for efficiency
- The example bitwise operations file demonstrates the encoding/decoding approach