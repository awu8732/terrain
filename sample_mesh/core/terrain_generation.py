import time
import numpy as np
from noise import pnoise2
from numba import njit
from pygame.locals import *
from OpenGL.GL import * 
from OpenGL.GLU import *

import configuration as config
import models.terrain
import utility

def generateHeightmap(width, depth, scale, octaves, persistence, lacunarity, base_seed):
    heights = np.zeros((width, depth))
    for x in range(width):
        for z in range(depth):
            nx = x / width * scale
            nz = z / depth * scale
            heights[x][z] = pnoise2(nx, nz, 
                                    octaves = octaves, 
                                    persistence = persistence,
                                    lacunarity = lacunarity, 
                                    base = base_seed)
    return heights

def generateMesh(heightmap):
    vertices = []
    indices = []
    width, depth = heightmap.shape
    ero_start = time.perf_counter()
    utility.resetErosionStatistics()

    if config.SIMULATE_EROSION:
        heightmap, config.STATS.TOTAL_D, config.STATS.TOTAL_E = simulateHydraulicErosion_numba(
            heightmap, 
            iterations = config.EROSION_ITERATIONS,
            initial_velocity = config.EROSION_INIT_VELOCITY)
        config.STATS.ERO_TIME = (time.perf_counter() - ero_start) * 1000
        utility.outputErosionStatistics()

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
    terrain = models.terrain.Terrain()
    vertices, indices = generateMesh(terrain.heightmap)
    config.STATS.VERTEX_COUNT = len(vertices)
    config.STATS.TRIANGLE_COUNT = len(indices) // 3
    config.STATS.GEN_TIME = (time.perf_counter() - gen_start) * 1000
    utility.updateStatsDisplay()

    #reset opengl view
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(-1 * config.HEIGHTMAP_WIDTH / 2, -0.06 * config.HEIGHTMAP_DEPTH, -1 * config.HEIGHTMAP_DEPTH)
    return vertices, indices, terrain.biome_map

def renderTerrain(vertices, indices, biome_map):
    glBegin(GL_TRIANGLES)
    for triangle in indices:
        for index in triangle:
            x, y, z = vertices[index]
            i = int(round(x))
            j = int(round(z))

            # Defensive check to stay in bounds
            if 0 <= i < biome_map.shape[0] and 0 <= j < biome_map.shape[1]:
                biome = biome_map[i][j]
                color = config.BIOME_COLORS.get(biome, (128, 128, 128))  # default gray
            else:
                color = (255, 0, 0)  # red = out-of-bounds error

            # Normalize to 0.0–1.0 for OpenGL
            r, g, b = [c - y * 0.1 for c in color]
            #print(r,g,b)
            glColor3f(r,g,b)
            glVertex3f(x, y, z)
    glEnd()

@njit
def simulateHydraulicErosion_numba(heightmap, 
                                         iterations=1000000, 
                                         initial_velocity = 0.0, 
                                         erosion_radius=3):
    hmap = heightmap.copy()
    width, height = hmap.shape
    total_d = 0.0
    total_e = 0.0

    for _ in range(iterations):
        x, y = np.random.randint(0, width), np.random.randint(0, height)
        d_vel = initial_velocity
        d_mass = 0.0
        d_water = 1.0

        for _ in range(30):  # max droplet lifetime
            x_int, y_int = int(x), int(y)

            # gradient calculation - bilinear interpolation
            if x_int < 0 or x_int >= width - 1 or y_int < 0 or y_int >= height - 1:
                dx = 0.0
                dy = 0.0
            else:
                xf, yf = x - x_int, y - y_int
                h00 = hmap[x_int, y_int]
                h10 = hmap[x_int+1, y_int]
                h01 = hmap[x_int, y_int+1]
                h11 = hmap[x_int+1, y_int+1]

                dx = (h10 - h00) * (1 - yf) + (h11 - h01) * yf
                dy = (h01 - h00) * (1 - xf) + (h11 - h10) * xf

                # clip manually
                dx = max(-10.0, min(10.0, dx))
                dy = max(-10.0, min(10.0, dy))

            normal = max(1e-6, np.sqrt(dx * dx + dy * dy))

            if dx == 0.0 and dy == 0.0:
                break

            x -= dx / normal
            y -= dy / normal

            if x < 0 or x >= width or y < 0 or y >= height:
                break

            x_int = int(x)
            y_int = int(y)

            slope = np.sqrt(dx * dx + dy * dy)
            s_capacity = d_vel * d_water * slope * 0.1

            if d_mass > s_capacity or hmap[x_int, y_int] < 0.0:
                deposit_amount = max(0.0, (d_mass - s_capacity) * 0.3)
                hmap[x_int, y_int] += deposit_amount
                d_mass -= deposit_amount
                total_d += deposit_amount
            else:
                erode_amount = min((s_capacity - d_mass) * 0.3, hmap[x_int, y_int] * 0.99)
                hmap[x_int, y_int] -= erode_amount
                d_mass += erode_amount
                total_e += erode_amount

            d_vel = max(0.0, d_vel + slope - 0.1)
            d_water *= 0.99
    
    return hmap, total_d, total_e
