import numpy as np
import configuration as config

class Terrain:
    def __init__(self):
        self.width = config.HEIGHTMAP_WIDTH
        self.depth = config.HEIGHTMAP_DEPTH
        self.scale = config.HEIGHTMAP_SCALE

        self.heightmap = np.zeros((self.width, self.depth))
        self.moisture_map = np.zeros((self.width, self.depth))
        self.temperature_map = np.zeros((self.width, self.depth))
        self.biome_map = np.full((self.width, self.depth), "", dtype=object)