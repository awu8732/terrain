# Procedural Terrain Generator

A real-time 3D terrain generation application using OpenGL and Python, featuring Perlin noise-based heightmaps, hydraulic erosion simulation, biome generation, and Blinn-Phong lighting.

## Features

- **Procedural Terrain Generation**: Uses Perlin noise with configurable octaves, persistence, and lacunarity
- **Hydraulic Erosion Simulation**: Optional physics-based erosion simulation using water droplet particles
- **Biome System**: Temperature and moisture-based biome classification with color mapping
- **Real-time Lighting**: Blinn-Phong shading model with configurable ambient, diffuse, and specular lighting
- **Interactive Controls**: Real-time parameter adjustment through DearPyGUI interface
- **Performance Monitoring**: Frame rate, generation time, and mesh statistics display

## Requirements

```
pygame
PyOpenGL
PyOpenGL_accelerate
dearpygui
numpy
noise
numba
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install pygame PyOpenGL PyOpenGL_accelerate dearpygui numpy noise numba
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Project Structure

```
sample_mesh/
├── main.py                 # Application entry point and main loop
├── configuration.py        # Global configuration constants
├── utility.py             # Utility functions and helpers
├── core/
│   ├── env_manager.py     # Environment setup and OpenGL initialization
│   ├── state.py           # Global application state
│   ├── terrain_generation.py  # Terrain generation and rendering logic
│   └── ui_manager.py      # User interface controls and callbacks
└── models/
    ├── mesh.py            # Mesh data structure
    ├── stats.py           # Performance statistics tracking
    └── terrain.py         # Terrain generation and biome calculation
```

## Configuration

Key parameters can be adjusted in `configuration.py`:

### Display Settings
- `WINDOW_WIDTH/HEIGHT`: Application window dimensions
- `WINDOW_FOV`: Field of view for 3D projection
- `ELEVATION_VIEW`: Camera elevation multiplier

### Heightmap Generation
- `HEIGHTMAP_WIDTH/DEPTH`: Terrain grid resolution
- `HEIGHTMAP_SCALE`: Vertical scaling factor
- `HEIGHTMAP_OCTAVES`: Number of noise octaves
- `HEIGHTMAP_PERSISTENCE`: Amplitude decay between octaves
- `HEIGHTMAP_LACUNARITY`: Frequency multiplier between octaves

### Erosion Simulation
- `SIMULATE_EROSION`: Enable/disable hydraulic erosion
- `EROSION_ITERATIONS`: Number of water droplets to simulate
- `EROSION_INIT_VELOCITY`: Initial velocity of water droplets

### Biome System
- `SIMULATE_BIOME`: Enable/disable biome coloring
- `BIOME_TEMPERATURE/MOISTURE`: Base temperature and moisture levels
- `BIOME_COLORS`: Color mapping for different biome types

### Lighting
- `LIGHTING_K_AMB/DIFF/SPEC`: Ambient, diffuse, and specular reflection coefficients
- `LIGHTING_SHIN`: Specular shininess factor

## Usage

1. Launch the application to see the initial randomly generated terrain
2. Use the control panel to adjust terrain parameters in real-time
3. Click "REGENERATE" to apply changes and generate new terrain
4. Monitor performance statistics in the stats panel

### Controls

- **Base Seed**: Random seed for terrain generation
- **Resolution**: Terrain grid size (affects performance)
- **Height Scale**: Vertical terrain scaling
- **Octaves**: Detail levels in noise generation
- **Persistence**: Height variation between octaves
- **Lacunarity**: Frequency scaling between octaves
- **Hydraulic Erosion**: Enable physics-based erosion simulation
- **Biome System**: Enable temperature/moisture-based coloring
- **Lighting Parameters**: Adjust Blinn-Phong lighting components

## Performance Notes

- Higher resolutions significantly impact performance
- Erosion & lighting simulation is computationally expensive (uses Numba JIT compilation)
- Frame rate and generation times are displayed in the stats panel
- Recommended starting resolution: 100x100 for real-time interaction

## Technical Details

### Terrain Generation
The terrain uses multi-octave Perlin noise to create natural-looking heightmaps. Each octave adds detail at different scales, controlled by persistence (amplitude decay) and lacunarity (frequency scaling).

### Hydraulic Erosion
Water droplets are simulated with basic physics including:
- Velocity and mass tracking
- Sediment carrying capacity based on velocity and slope
- Deposition when capacity is exceeded
- Erosion when capacity allows

### Biome Classification
Biomes are determined using a temperature-moisture matrix:
- Temperature influenced by height (cooler at altitude)
- Moisture generated using separate Perlin noise
- Seven biome types: Tundra, Taiga, Temperate, Grassland, Desert, Savanna, Rainforest

### Lighting Model
Blinn-Phong lighting provides realistic shading with:
- Surface normals calculated from heightmap gradients
- Configurable ambient, diffuse, and specular components
- Optimized using Numba for real-time performance