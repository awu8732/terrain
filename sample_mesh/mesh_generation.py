from pygame.locals import *
from OpenGL.GL import * 
from OpenGL.GLU import *
from noise import pnoise2
import numpy as np
import config

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
            config.STATS_ITER_COUNT += 1
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

            config.STATS_ITER_COUNT += 1

    #assign generic triangle indices
    for x in range(width - 1):
        for z in range(depth - 1):
            top_left = x * depth + z
            top_right = (x + 1) * depth + z
            bottom_left = x * depth + (z + 1)
            bottom_right = (x + 1) * depth + (z + 1)

            indices.append((top_left, bottom_left, top_right))
            indices.append((top_right, bottom_left, bottom_right))

            config.STATS_ITER_COUNT += 1
            config.STATS_TRIANGLE_COUNT += 1

    return vertices, indices

def renderTerrain(vertices, indices):
    glBegin(GL_TRIANGLES)
    for triangle in indices:
        for index in triangle:
            vertex = vertices[index]
            glColor3f(0.3, 0.8 - vertex[1] * 0.1, 0.3)
            glVertex3fv(vertex)
            config.STATS_ITER_COUNT += 1
    glEnd()