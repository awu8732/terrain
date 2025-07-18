import numpy as np
import configuration as config
import core.terrain_generation

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