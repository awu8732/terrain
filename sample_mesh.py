import pygame
from pygame.locals import *
from OpenGL.GL import * 
from OpenGL.GLU import *
from noise import pnoise2
import numpy as np

#don't forget BASE


def generateHeightmap(width, depth, scale, octaves=4, persistence=0.5, lacunarity=2.0):
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

def generateMesh(heightmap, scale = 5):
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

def initializeEnvironment():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(90, display[0] / display[1], 0.1, 1000.0)
    glTranslatef(-50, -10, -100)  # Adjust camera
    glEnable(GL_DEPTH_TEST)

def main():
    initializeEnvironment()
    # Generate terrain
    heightmap = generateHeightmap(100, 100, scale=10)
    vertices, indices = generateMesh(heightmap, scale = 10)

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

