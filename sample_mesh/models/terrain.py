from noise import pnoise2
import numpy as np

import configuration as config
import core.terrain_generation
import utility

class Terrain:
    def __init__(self):
        self.width = config.HEIGHTMAP_WIDTH
        self.depth = config.HEIGHTMAP_DEPTH
        self.scale = config.HEIGHTMAP_SCALE

        self.heightmap = np.zeros((self.width, self.depth))
        self.moisture_map = np.zeros((self.width, self.depth))
        self.temperature_map = np.zeros((self.width, self.depth))
        self.biome_map = np.full((self.width, self.depth), "", dtype=object)

        self._setup()

    def _setup(self):
        self._generateHeightmap()
        self._generateTemperatureMap()
        self._generateMoistureMap()
        self._assignBiomes()

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
    
    def _generateTemperatureMap(self):
        for x in range(self.width):
            for z in range(self.depth):
                latitude = z / self.depth  # simulate "latitude"
                elevation = self.heightmap[x][z]
                temp = 1.0 - abs(latitude - 0.5) * 2
                temp -= elevation * 0.5
                self.temperature_map[x][z] = np.clip(temp, 0.0, 1.0)

    def _generateMoistureMap(self):
        moisture_scale = 5.0  # adjustable
        for x in range(self.width):
            for z in range(self.depth):
                nx = x / self.width * moisture_scale
                nz = z / self.depth * moisture_scale
                moisture = pnoise2(nx, nz, 
                                   octaves=2, 
                                   base=config.HEIGHTMAP_BASE_SEED)
                self.moisture_map[x][z] = np.clip((moisture + 1) / 2, 0.0, 1.0)

    def _assignBiomes(self):
        for x in range(self.width):
            for z in range(self.depth):
                t = self.temperature_map[x][z]
                m = self.moisture_map[x][z]
                self.biome_map[x][z] = utility.getBiome(t,m)