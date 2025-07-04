import pygame
from pygame.locals import *
from OpenGL.GL import * 
from OpenGL.GLU import *
import random as rand
from mesh_generation import *
import config

def configureEnvironment():
    pygame.init()
    display = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(config.WINDOW_FOV, display[0] / display[1],
                    config.WINDOW_CLIPPING_NEAR, config.WINDOW_CLIPPING_FAR)
    glTranslatef(-50, -10, -100)  # Adjust camera
    glEnable(GL_DEPTH_TEST)

    config.HEIGHTMAP_BASE_SEED = rand.randint(1, 500)

def printTerrainLogger():
    print("****** TERRAIN OUTPUT LOGGER ******")
    print(f"SEED_BASE: {config.HEIGHTMAP_BASE_SEED}")
    print(f"ITER_COUNT: {config.STATS_ITER_COUNT}")
    print(f"TRIANGLE_COUNT: {config.STATS_TRIANGLE_COUNT}")

def main():
    configureEnvironment()
    # Generate terrain
    heightmap = generateHeightmap(config.HEIGHTMAP_WIDTH, config.HEIGHTMAP_DEPTH)
    vertices, indices = generateMesh(heightmap)

    # Rotation
    angle = 0
    clock = pygame.time.Clock()
    running = True

    printTerrainLogger()

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

