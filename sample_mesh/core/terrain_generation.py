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
    normals = []
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

    dzdx, dzdy = np.gradient(heightmap)
    #generate vertice list & normal map
    for x in range(width):
        for z in range(depth):
            y = heightmap[x][z] * config.HEIGHTMAP_SCALE
            vertices.append((x,y,z))

            # Normal from gradient
            nx = -dzdx[x][z]
            ny = 1.0
            nz = -dzdy[x][z]
            normal = np.array([nx, ny, nz])
            normal /= np.linalg.norm(normal)
            normals.append(tuple(normal))

    #assign generic triangle indices
    for x in range(width - 1):
        for z in range(depth - 1):
            top_left = x * depth + z
            top_right = (x + 1) * depth + z
            bottom_left = x * depth + (z + 1)
            bottom_right = (x + 1) * depth + (z + 1)

            indices.append((top_left, bottom_left, top_right))
            indices.append((top_right, bottom_left, bottom_right))

    return vertices, indices, normals

def regenerateTerrain():   
    gen_start = time.perf_counter()
    terrain = models.terrain.Terrain()
    vertices, indices, normals = generateMesh(terrain.heightmap)
    config.STATS.VERTEX_COUNT = len(vertices)
    config.STATS.TRIANGLE_COUNT = len(indices) // 3
    config.STATS.GEN_TIME = (time.perf_counter() - gen_start) * 1000
    utility.updateStatsDisplay()

    #reset opengl view
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(-1 * config.HEIGHTMAP_WIDTH / 2, -0.06 * config.HEIGHTMAP_DEPTH, -1 * config.HEIGHTMAP_DEPTH)
    return vertices, indices, normals, terrain.biome_map

def renderTerrain(vertices, indices, normals, biome_map):
    light_dir = np.array([1.0, 1.0, 0.8])
    light_dir = light_dir / np.linalg.norm(light_dir)
    view_dir = np.array([0.0, 1.0, 1.0])
    view_dir = view_dir / np.linalg.norm(view_dir)

    intensities = computeBlinnPhongIntensities_numba(
        np.array(normals),
        config.LIGHTING_L_DIR,
        config.LIGHTING_V_DIR,
        config.LIGHTING_K_AMB,
        config.LIGHTING_K_DIFF,
        config.LIGHTING_K_SPEC,
        config.LIGHTING_SHIN
    )

    glBegin(GL_TRIANGLES)
    for triangle in indices:
        for index in triangle:
            vertex = vertices[index]
            if config.SIMULATE_BIOME:
                base_color = utility.getBiomeColorFromVertex(vertices[index], biome_map)
                shaded_color = np.array(base_color) * intensities[index]

                glColor3f(*shaded_color)
                glVertex3f(*vertex)
            else:
                glColor3f(0.3 + vertex[1] * 0.02, 0.30 + vertex[1] * 0.1, 0.3)
                glVertex3fv(vertex)
    glEnd()

@njit
def computeBlinnPhongIntensities_numba(normals, light_dir, view_dir, 
                                     k_ambient, k_diffuse, k_specular, shininess):
    intensities = np.zeros(normals.shape[0])
    half_vec = (light_dir + view_dir)
    half_vec /= np.linalg.norm(half_vec)

    for i in range(normals.shape[0]):
        norm = normals[i]
        dot_nl = np.dot(norm, light_dir)
        dot_nh = np.dot(norm, half_vec)

        ambient = k_ambient
        diffuse = k_diffuse * max(dot_nl, 0.0)
        specular = k_specular * (max(dot_nh, 0.0) ** shininess)
        intensity = ambient + diffuse + specular

        intensities[i] = min(1.0, max(0.0, intensity))
    return intensities

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
