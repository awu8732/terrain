import time
import numpy as np
from noise import pnoise2
from pygame.locals import *
from OpenGL.GL import * 
from OpenGL.GLU import *

import configuration as config
import utility

def generateHeightmap():
    heights = np.zeros((config.HEIGHTMAP_WIDTH, config.HEIGHTMAP_DEPTH))
    for x in range(config.HEIGHTMAP_WIDTH):
        for z in range(config.HEIGHTMAP_DEPTH):
            nx = x / config.HEIGHTMAP_WIDTH * config.HEIGHTMAP_SCALE
            nz = z / config.HEIGHTMAP_DEPTH * config.HEIGHTMAP_SCALE
            heights[x][z] = pnoise2(nx, nz, 
                                    octaves = config.HEIGHTMAP_OCTAVES, 
                                    persistence = config.HEIGHTMAP_PERSISTENCE,
                                    lacunarity = config.HEIGHTMAP_LACUNARITY, 
                                    base = config.HEIGHTMAP_BASE_SEED)
    return heights

def generateMesh(heightmap):
    vertices = []
    indices = []
    width, depth = heightmap.shape

    #generate vertice list
    for x in range(width):
        for z in range(depth):
            y = heightmap[x][z] * config.HEIGHTMAP_SCALE
            vertices.append((x,y,z))

    #assign generic triangle indices
    for x in range(width - 1):
        for z in range(depth - 1):
            top_left = x * depth + z
            top_right = (x + 1) * depth + z
            bottom_left = x * depth + (z + 1)
            bottom_right = (x + 1) * depth + (z + 1)

            indices.append((top_left, bottom_left, top_right))
            indices.append((top_right, bottom_left, bottom_right))

    return vertices, indices

def regenerateTerrain():   
    gen_start = time.perf_counter()
    heightmap = generateHeightmap()
    vertices, indices = generateMesh(heightmap)
    config.STATS.VERTEX_COUNT = len(vertices)
    config.STATS.TRIANGLE_COUNT = len(indices) // 3
    config.STATS.GEN_TIME = (time.perf_counter() - gen_start) * 1000
    utility.updateStatsDisplay()

    #reset opengl view
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(-1 * config.HEIGHTMAP_WIDTH / 2, -0.06 * config.HEIGHTMAP_DEPTH, -1 * config.HEIGHTMAP_DEPTH)
    return vertices, indices

def renderTerrain(vertices, indices):
    glBegin(GL_TRIANGLES)
    for triangle in indices:
        for index in triangle:
            vertex = vertices[index]
            glColor3f(0.3, 0.8 - vertex[1] * 0.1, 0.3)
            glVertex3fv(vertex)
    glEnd()

def simulateHydraulicErosion(heightmap, iterations = 100000, erosion_radius = 3):
    hmap = heightmap.copy()
    width, height = hmap.shape

    for _ in range(iterations):
        x, y = np.random.randint(0, width), np.random.randint(0, height)

        #put droplet properties here
        for _ in range(30): # max droplet lifetime
            pass