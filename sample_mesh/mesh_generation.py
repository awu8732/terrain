import time
import numpy as np
from noise import pnoise2
from numba import njit
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
    ero_start = time.perf_counter()
    utility.resetErosionStatistics()

    if config.SIMULATE_EROSION:
        heightmap, config.STATS.TOTAL_D, config.STATS.TOTAL_E = simulateHydraulicErosion_accelerated(heightmap, config.EROSION_ITERATIONS)
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

# CPU non-accelerated method
def simulateHydraulicErosion(heightmap, iterations = 20000, erosion_radius = 3):
    hmap = heightmap.copy()
    width, height = hmap.shape

    for _ in range(iterations):
        x, y = np.random.randint(0, width), np.random.randint(0, height)
        d_vel = 0.0
        d_mass = 0.0
        d_water = 1.0

        #put droplet properties here
        for _ in range(30): # max droplet lifetime
            x_int, y_int = int(x), int(y)
            dx, dy = utility.calculateGradient(hmap, x, y, x_int, y_int, width, height)
            normal = max(1e-6, np.sqrt(dx * dx + dy * dy))

            if dx == 0 and dy == 0:
                break
            x -= dx / normal
            y -= dy / normal

            # compute sediment capacity (higher velocity = more carrying capacity)
            slope = np.sqrt(dx * dx + dy * dy)
            s_capacity = d_vel * d_water * slope * 0.1

            if d_mass > s_capacity or hmap[x_int, y_int] < 0:
                deposit_amount = max(0.0, (d_mass - s_capacity) * 0.3)
                hmap[x_int, y_int] += deposit_amount
                d_mass -= deposit_amount
                config.STATS.TOTAL_D += deposit_amount
            else: 
                erode_amount = min((s_capacity - d_mass) * 0.3, hmap[x_int, y_int] * 0.99)
                hmap[x_int, y_int] -= erode_amount
                d_mass += erode_amount
                config.STATS.TOTAL_E += erode_amount

            d_vel = max(0, d_vel + np.sqrt(dx * dx + dy * dy) - 0.1)
            d_water *= 0.99
    print(f"TOTAL DEPOSITED: {config.STATS.TOTAL_D}")
    print(f"TOTAL ERODED: {config.STATS.TOTAL_E}")
    return hmap

@njit
def simulateHydraulicErosion_accelerated(heightmap, iterations=1000000, erosion_radius=3):
    hmap = heightmap.copy()
    width, height = hmap.shape

    total_d = 0.0
    total_e = 0.0

    for _ in range(iterations):
        x, y = np.random.randint(0, width), np.random.randint(0, height)
        d_vel = 0.0
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
