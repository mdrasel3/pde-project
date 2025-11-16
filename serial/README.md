# HPP Model Simulation with Reflective Boundaries

This program provides a user interface to run a simulation of the **HPP model** (a lattice gas automaton) with reflective boundaries. Users can initialize the grid size, place particles randomly or manually, and visualize the simulation.

## Prerequisites

- **Python 3.x** is required.
- Install the required Python packages by running:
  ```bash
   pip install -r requirements.txt
   ```
- The following Python packages and modules must be available:
  - `grid.py` (containing `HPPGrid` class)
  - `animation.py` (containing `HPPVisualizer` class)
  - `random` (standard library)

Make sure all modules are in the correct directories:
- The file `grid.py` and `animation.py` should be in the same folder as `main.py`.

## Installation

1. Place `main.py`, `grid.py`, and `animation.py` in the same root project directory.
2. (Optional) Create and activate a Python virtual environment:
   - **Windows:**
     ```bat
     python -m venv venv
     venv\Scripts activate
     ```
   - **Linux/macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
## Running the Simulation

You can start the simulation by running:

```bash
python main.py
```

## Usage Instructions

- On startup, you will be prompted to **enter a grid side length** (e.g., 5, 10, 20). Minimum size is 3.
- Choose **random** or **manual** particle placement:
  - **Random:** The program asks for the number of particles to place randomly on the grid.
  - **Manual:** You enter coordinate, direction triplets (row col direction), using `u` (up), `d` (down), `r` (right), `l` (left). Enter `-1` to finish adding particles.
- The visualization window will appear, showing the simulation. **Close the window** to continue.
- You will be prompted to **save the animation as a GIF**.

## Notes

- **Error Handling:** If invalid input is given, you'll be prompted to try again.
- **Simulation Visualization:** Uses the `HPPVisualizer` for animated output.
- **Boundary Behavior:** Particles bounce off the grid edges (reflective), do not wrap around.

---

**Example Directory Structure:**
```
/your_project/
│
├── main.py
├── grid.py
└── animation.py
```
