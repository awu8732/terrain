import pygame
from pygame.locals import *
from OpenGL.GL import * 
from OpenGL.GLU import *
from noise import pnoise2
import numpy as np

#don't forget BASE
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_FOV = 90
WINDOW_CLIPPING_NEAR = 0.1
WINDOW_CLIPPING_FAR = 1000.0

HEIGHTMAP_WIDTH = 100
HEIGHTMAP_DEPTH = 100
HEIGHTMAP_SCALE_DEFAULT = 10
HEIGHTMAP_OCTAVES_DEFAULT = 10
HEIGHTMAP_PERSISTENCE_DEFAULT = 0.5
HEIGHTMAP_LACUNARITY_DEFAULT = 2.0


def generateHeightmap(width, depth, 
                      scale = HEIGHTMAP_SCALE_DEFAULT,
                      octaves = HEIGHTMAP_OCTAVES_DEFAULT, 
                      persistence = HEIGHTMAP_PERSISTENCE_DEFAULT,
                      lacunarity = HEIGHTMAP_LACUNARITY_DEFAULT):
    heights = np.zeros((width, depth))
    for x in range(width):
        for z in range(depth):
            nx = x / width * scale
            nz = z / depth * scale
            heights[x][z] = pnoise2(nx, 
                                    nz, 
                                    octaves = octaves, 
                                    persistence = persistence,
                                    lacunarity = lacunarity)
    return heights

def generateMesh(heightmap, 
                 scale = HEIGHTMAP_SCALE_DEFAULT):
    vertices = []
    indices = []
    width, depth = heightmap.shape

    #generate vertice list
    for x in range(width):
        for z in range(depth):
            y = heightmap[x][z] * scale
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

def renderTerrain(vertices, indices):
    glBegin(GL_TRIANGLES)
    for triangle in indices:
        for index in triangle:
            vertex = vertices[index]
            glColor3f(0.3, 0.8 - vertex[1] * 0.1, 0.3)
            glVertex3fv(vertex)
    glEnd()

def configureEnvironment():
    pygame.init()
    display = (WINDOW_WIDTH, WINDOW_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(WINDOW_FOV, display[0] / display[1], WINDOW_CLIPPING_NEAR, WINDOW_CLIPPING_FAR)
    glTranslatef(-50, -10, -100)  # Adjust camera
    glEnable(GL_DEPTH_TEST)

def main():
    configureEnvironment()
    # Generate terrain
    heightmap = generateHeightmap(HEIGHTMAP_WIDTH, HEIGHTMAP_DEPTH)
    vertices, indices = generateMesh(heightmap)

    # Rotation
    angle = 0
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        delta_time = clock.tick(60) / 1000
        angle += 20 * delta_time

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        #glRotatef(angle, 0, 1, 0)
        renderTerrain(vertices, indices)
        glPopMatrix()

        pygame.display.flip()

    pygame.quit()

main()

