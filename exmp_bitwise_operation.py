# Author: rasel
# Demonstration of bitwise operation 

# Directions (bit indices)
RIGHT, UP, LEFT, DOWN = 0, 1, 2, 3
DIRECTION_NAMES = {RIGHT: "Right (→)", UP: "Up (↑)", LEFT: "Left (←)", DOWN: "Down (↓)"}

def encode_particles(present_directions):
    """
    Encode a list of present directions into a single integer (bitwise).
    Example: [RIGHT, LEFT] => 0b0101 (decimal 5)
    """
    cell = 0
    for d in present_directions:
        cell |= (1 << d)
    return cell

def decode_particles(cell):
    """
    Given a cell integer, return the list of present directions.
    Example: 0b1010 => [UP, DOWN]
    """
    return [d for d in range(4) if cell & (1 << d)]

# ---- Demo Usage ----

# 1. Encode some direction lists:
particles = [
    [],
    [RIGHT],
    [UP, DOWN],
    [RIGHT, LEFT],
    [RIGHT, UP, LEFT, DOWN]
]

print("Encoding demonstration:\n")
for p in particles:
    cell = encode_particles(p)
    bits = format(cell, '04b')
    print(f"Directions: {[DIRECTION_NAMES[d] for d in p]} --> Encoded integer: {cell} (binary: {bits})")

print("\nDecoding demonstration:\n")
# 2. Decode some cell values:
cell_values = [0, 1, 2, 5, 10, 15]
for val in cell_values:
    present = decode_particles(val)
    print(f"Cell value: {val} (binary: {format(val, '04b')}) --> Directions: {[DIRECTION_NAMES[d] for d in present]}")

# 3. Add/remove/check directions:
print("\nBitwise operations demonstration:\n")
cell = 0  # Start empty
print(f"Initial: {format(cell, '04b')}")
# Add RIGHT
cell |= (1 << RIGHT)
print(f"Add RIGHT: {format(cell, '04b')}")
# Add UP
cell |= (1 << UP)
print(f"Add UP: {format(cell, '04b')}")
# Remove RIGHT
cell &= ~(1 << RIGHT)
print(f"Remove RIGHT: {format(cell, '04b')}")
# Check for UP
if cell & (1 << UP):
    print("UP is present in cell.")
