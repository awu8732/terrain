from noise import pnoise2
import numpy as np
#import matplotlib.pyplot as plt

import configuration as config
import core.terrain_generation
import utility

class Terrain:
    def __init__(self):
        self.width = config.HEIGHTMAP_WIDTH
        self.depth = config.HEIGHTMAP_DEPTH
        self.scale = config.HEIGHTMAP_SCALE

        self.heightmap = np.zeros((self.width, self.depth))
        self.normal_map = np.zeros((self.width * self.depth, 3), dtype=np.float32)
        self.moisture_map = np.zeros((self.width, self.depth))
        self.temperature_map = np.zeros((self.width, self.depth))
        self.biome_map = np.full((self.width, self.depth), "", dtype=object)

        self._setup()

    def _setup(self):
        self._generateHeightmap()
        self._generateTemperatureMap()
        self._generateMoistureMap()
        self._assignBiomes()
    
    def _computeNormals(self):
        index = 0
        dzdx, dzdy = np.gradient(self.heightmap)

        for x in range(self.width):
            for z in range(self.depth):
                # Normal from slope
                nx = -dzdx[x][z]
                ny = 1.0
                nz = -dzdy[x][z]
                normal = np.array([nx, ny, nz])
                normal /= np.linalg.norm(normal)
                self.normal_map[index] = normal
                index+=1

    def _generateHeightmap(self):
        self.heightmap = core.terrain_generation.generateHeightmap(
            self.width,
            self.depth,
            self.scale,
            config.HEIGHTMAP_OCTAVES,
            config.HEIGHTMAP_PERSISTENCE,
            config.HEIGHTMAP_LACUNARITY,
            config.HEIGHTMAP_BASE_SEED
        )
        self._computeNormals()
    
    def _generateTemperatureMap(self):
        frequency = 3.0 / min(self.width, self.depth)
        for x in range(self.width):
            for z in range(self.depth):
                nx = x * frequency
                nz = z * frequency
                perlin_t = (pnoise2(nx, nz, octaves=3, base=config.HEIGHTMAP_BASE_SEED) + 1.05) / 2.0  # range [0, 1]
                abs_height = (self.heightmap[x][z] + 1) / 2
                calc_t = perlin_t * (1.0 - abs_height * 0.2) * config.BIOME_TEMPERATURE

                self.temperature_map[x][z] = np.clip(calc_t, 0.0, 1.0)

        # plt.imshow(self.temperature_map, cmap="plasma", origin="lower")
        # plt.colorbar(label="Temperature")
        # plt.show()

    def _generateMoistureMap(self):
        frequency = 3.0 / min(self.width, self.depth)
        for x in range(self.width):
            for z in range(self.depth):
                nx = x * frequency
                nz = z * frequency
                perlin_m = pnoise2(nx, nz, octaves=3, base=config.HEIGHTMAP_BASE_SEED)
                abs_height = (self.heightmap[x][z] + 1) / 2
                calc_m = perlin_m  / 2.0 + config.BIOME_MOISTURE ** 2 - abs_height * 0.2 + 0.05
                self.moisture_map[x][z] = np.clip(calc_m, 0.0, 1.0)

        # plt.imshow(self.moisture_map, cmap="viridis", origin="lower")
        # plt.colorbar(label="Moisture Level")
        # plt.show()

    def _assignBiomes(self):
        for x in range(self.width):
            for z in range(self.depth):
                t = self.temperature_map[x][z]
                m = self.moisture_map[x][z]
                self.biome_map[x][z] = utility.getBiome(t,m)