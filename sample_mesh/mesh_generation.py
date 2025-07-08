from pygame.locals import *
from OpenGL.GL import * 
from OpenGL.GLU import *
from noise import pnoise2
import numpy as np
import config

def generateHeightmap(width, depth, 
                      scale = config.HEIGHTMAP_SCALE,
                      octaves = config.HEIGHTMAP_OCTAVES, 
                      persistence = config.HEIGHTMAP_PERSISTENCE,
                      lacunarity = config.HEIGHTMAP_LACUNARITY):
    heights = np.zeros((width, depth))
    for x in range(width):
        for z in range(depth):
            nx = x / width * scale
            nz = z / depth * scale
            heights[x][z] = pnoise2(nx, 
                                    nz, 
                                    octaves = octaves, 
                                    persistence = persistence,
                                    lacunarity = lacunarity, 
                                    base = 10)
            config.STATS_ITER_COUNT += 1
    return heights

def generateMesh(heightmap, 
                 scale = config.HEIGHTMAP_SCALE):
    vertices = []
    indices = []
    width, depth = heightmap.shape

    #generate vertice list
    for x in range(width):
        for z in range(depth):
            y = heightmap[x][z] * scale
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