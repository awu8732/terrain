import numpy as np
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from noise import pnoise2
from noise import snoise2

#base --> seed for generator
seed_base = random.randint(1,1000)
print(f"Seed Base: {seed_base}")

# fBm generator
def fBm(x, y, octaves, persistence, lacunarity, scale):
    value = 0.0
    frequency = 1.0
    amplitude = 1.0
    max_value = 0.0
    for _ in range(octaves):
        value += amplitude * snoise2(x * frequency / scale, y * frequency / scale, base = seed_base)
        max_value += amplitude
        amplitude *= persistence
        frequency *= lacunarity
    return value / max_value

# PARAMETERS
width, height = 100, 100
scale = 100.0
octaves = 5
persistence = 0.5
lacunarity = 2.0

# Generate coordinate grid & heightmap z
x = np.linspace(0, width, width)
y = np.linspace(0, height, height)
x, y = np.meshgrid(x, y)

z = np.zeros((height, width))
for i in range(height):
    for j in range(width):
        z[i][j] = fBm(j, i, octaves, persistence, lacunarity, scale)

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(x, y, z, cmap='terrain', linewidth=0, antialiased=True)
fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)

# Set labels
ax.set_title("3D Terrain Heightmap (fBM)")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Height")
ax.view_init(elev=45, azim=135)

plt.show()