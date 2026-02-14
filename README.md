Fish-Predator: High-Performance Boid Simulation

A high-performance flocking simulation using a C++ physics engine exposed to Python via pybind11. This project implements Craig Reynolds' boid algorithms with significant optimizations, including OpenMP parallelization and Spatial Partitioning via a uniform grid.

🚀 Key Features

C++ Backend: Heavy lifting (physics, collision, and neighbor lookups) is handled in C++ for maximum performance.

Parallel Execution: Uses OpenMP to parallelize boid updates across multiple CPU cores.

Grid-Based Spatial Partitioning: Replaces the $O(n^2)$ naive search with a highly efficient $O(n)$ grid lookup, allowing for thousands of boids at high framerates.

Vectorized Data Transfer: Uses NumPy-compatible memory buffers to pass state between C++ and Python without expensive copying.

Predator Interaction: Real-time avoidance behavior where boids flee from the mouse cursor.

🛠 Tech Stack

Core: C++11

Interface: pybind11

Parallelism: OpenMP

Visuals: Python (Pygame)

Math: NumPy

📂 Project Structure

src/engine/: C++ Headers (Boid.h, Grid.h, Vector2D.h, simulation.h)

src/bindings.cpp: Pybind11 glue code for the Python extension.

scripts/gui.py: Main entry point with Pygame visualization.

setup.py: Build script for the C++ extension module.

tests/: Performance benchmarking and behavior validation scripts.

⚙️ Installation & Building

Prerequisites

Python 3.12+

A C++ compiler (MSVC, GCC, or Clang)

OpenMP installed on your system

Build the Module

To compile the boid_engine extension:

```Bash
pip install .
```

Or build in-place for development:

```Bash
python setup.py build_ext --inplace
```

🎮 Running the Simulation

Execute the main GUI script:

```Bash
python scripts/gui.py
```


🔬 Performance Optimizations

1. Spatial Partitioning

The simulation implements a Grid class that divides the screen into cells. Each boid only checks its immediate 3x3 cell neighborhood for flockmates, drastically reducing the number of distance calculations per frame.

2. OpenMP Threading

The update loop in simulation.h is parallelized:

```C++
#pragma omp parallel for schedule(static)
for (int i = 0; i < n; ++i) {
    // Parallel physics calculations
}
```

This allows the simulation to scale linearly with your CPU's core count.

3. Rendering Pipeline

gui.py uses pygame.surfarray for fast pixel manipulation and NumPy's vectorized operations to calculate fish orientations, ensuring the visualization isn't a bottleneck for the C++ engine.

📊 Configuration

You can tune the simulation in scripts/gui.py:

BOID_COUNT: Set the number of boids (e.g., 5,000 to 10,000).

OMP_NUM_THREADS: Adjust the thread count for the physics engine.