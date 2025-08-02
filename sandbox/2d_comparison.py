import numpy as np
import random
import matplotlib.pyplot as plt
from noise import snoise2
from noise import pnoise2

#base --> seed for generator
seed_base = random.randint(1,1000)
print(f"Seed Base: {seed_base}")

#persistence --> recursion AMPLITUDE of octaves
#lacunarity  --> recursion FREQUENCY of octaves

def fBm(x, y, octaves, persistence, lacunarity, scale):
    value = 0.0
    frequency = 1.0
    amplitude = 1.0
    max_value = 0.0
    
    for __ in range(octaves):
        value += amplitude * snoise2(x * frequency / scale, y * frequency / scale, base=seed_base)
        max_value += amplitude
        amplitude *= persistence
        frequency *= lacunarity

    return value / max_value

# Generate terrain
width, height = 100, 100
terrain1 = np.zeros((height, width))
for y in range(height):
    for x in range(width):
        terrain1[y][x] = fBm(x, y, octaves=5, persistence=1.0, lacunarity=1.5, scale=100.0)

terrain2= np.zeros((height, width))
for y in range(height):
    for x in range(width):
        terrain2[y][x] = fBm(x, y, octaves=5, persistence=1.0, lacunarity=2.0, scale=100.0)

terrain3= np.zeros((height, width))
for y in range(height):
    for x in range(width):
        terrain3[y][x] = fBm(x, y, octaves=5, persistence=1.0, lacunarity=2.5, scale=100.0)


# Set up subplots: 1 row, 3 columns
fig, axs = plt.subplots(1, 3, figsize=(15, 5))  # 3 plots side-by-side
fig.suptitle("Different Terrain Colormaps", fontsize=16)\

#'terrain', 'gray', 'viridis', 'plasma', 'magma', 'cividis
terrains = [terrain1, terrain2, terrain3]

for i in range(len(terrains)):
    img = axs[i].imshow(terrains[i], cmap="terrain")
    axs[i].set_title(f"Sample {i}")
    axs[i].axis('off')
    plt.colorbar(img, ax=axs[i], shrink=0.7)

plt.show()