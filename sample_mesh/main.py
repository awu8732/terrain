import pygame
from pygame.locals import *
from OpenGL.GL import * 
from OpenGL.GLU import *
import random as rand
from mesh_generation import *
import config
import dearpygui.dearpygui as dpg

def configureEnvironment():
    pygame.init()
    display = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(config.WINDOW_FOV, display[0] / display[1],
                    config.WINDOW_CLIPPING_NEAR, config.WINDOW_CLIPPING_FAR)
    glTranslatef(-50, -10, -100)
    glEnable(GL_DEPTH_TEST)

    config.HEIGHTMAP_BASE_SEED = rand.randint(1, 500)

    #Initialize Dear PyGUI
    dpg.create_context()
    initializeTerrainControls()
    dpg.create_viewport(title = "TERRAIN CONTROLS", width = 400, height = 600)
    dpg.setup_dearpygui()
    dpg.show_viewport()

def initializeTerrainControls():
    with dpg.window(label = "Terrain Parameters", width = 400, height = 600):
        dpg.add_slider_float(label = "Height Scale",
                             default_value = 1.0, 
                             min_value = 0.1, 
                             max_value = 5.0, 
                             tag = "height_scale")
        # Stats display
        dpg.add_text("Terrain Stats:")
        dpg.add_text(f"Triangles: {config.STATS_TRIANGLE_COUNT}", tag="tri_count")
        dpg.add_text(f"Iterations: {config.STATS_ITER_COUNT}", tag="iter_count")

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
        dpg.render_dearpygui_frame()
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

    dpg.destroy_context()
    pygame.quit()

if __name__ == "__main__":
    main()
