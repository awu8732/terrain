import dearpygui.dearpygui as dpg
import logging
from OpenGL.GL import * 
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import random as rand

import config
from mesh_generation import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]  # Send to terminal
)
logger = logging.getLogger("TERRAIN")

def configureEnvironment():
    pygame.init()
    display = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
    
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    config.HEIGHTMAP_BASE_SEED = rand.randint(1, 500)

    #Initialize OpenGL and DearPy
    gluPerspective(config.WINDOW_FOV, display[0] / display[1],
                    config.WINDOW_CLIPPING_NEAR, config.WINDOW_CLIPPING_FAR)
    glTranslatef(-50, -10, -100)
    glEnable(GL_DEPTH_TEST)

    dpg.create_context()
    initializeTerrainControls()
    dpg.create_viewport(title = "TERRAIN CONTROLS", width = 400, height = 520)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    logger.info("Environment configuration complete")

def cleanupEnvironment():
    dpg.destroy_context()
    pygame.quit()

def initializeTerrainControls():
    logger.info("Initializing terrain control panel..")
    with dpg.window(label = "Terrain Parameters", width = 400, height = 300, pos = (0,0),
                    no_close = True, no_collapse = True, no_move = True):
        dpg.add_input_int(label = "Base Seed",
                             default_value = config.HEIGHTMAP_BASE_SEED,
                             tag = "seed_input",
                             callback = updateTerrainParameters)
        dpg.add_slider_float(label = "Height Scale",
                             default_value = config.HEIGHTMAP_SCALE, 
                             min_value = 0.1, 
                             max_value = 30.0, 
                             tag = "scale",
                             callback = updateTerrainParameters)
        dpg.add_slider_int(label = "Octaves",
                             default_value = config.HEIGHTMAP_OCTAVES, 
                             min_value = 1, 
                             max_value = 20, 
                             tag = "octaves",
                             callback = updateTerrainParameters)
        dpg.add_slider_float(label = "Persistence",
                             default_value = config.HEIGHTMAP_PERSISTENCE, 
                             min_value = 0.1, 
                             max_value = 1.0, 
                             tag = "persistence",
                             callback = updateTerrainParameters)
        dpg.add_slider_float(label = "Lacunarity",
                             default_value = config.HEIGHTMAP_LACUNARITY, 
                             min_value = 1.0, 
                             max_value = 4.0, 
                             tag = "lacunarity",
                             callback = updateTerrainParameters)
        
        dpg.add_button(label = "REGNERATE", callback = requestTerrainRegeneration)

    with dpg.window(label = "Terrain Stats", width = 400, height = 200, pos = (0, 310),
                    no_close = True, no_collapse = True, no_move = True):
        dpg.add_text(f"Triangles: {config.STATS_TRIANGLE_COUNT}", tag="tri_count")
        dpg.add_text(f"Iterations: {config.STATS_ITER_COUNT}", tag="iter_count")

def terrainParamsToLogger(onStart = False):
    message = "Regeneration successful"
    if onStart:
        message = "Initial terrain"
    logger.info(
        f"\033[0m{message}: \033[0m | "
        f"\033[36mSeed\033[0m: {config.HEIGHTMAP_BASE_SEED} | "
        f"\033[36mRes\033[0m: {config.HEIGHTMAP_WIDTH}x{config.HEIGHTMAP_DEPTH}|\n"
        f"    \033[33mScale\033[0m={round(config.HEIGHTMAP_SCALE, 2)} "
        f"\033[33mOctaves\033[0m={config.HEIGHTMAP_OCTAVES} "
        f"\033[33mPersist\033[0m={round(config.HEIGHTMAP_PERSISTENCE, 3)} "
        f"\033[33mLacun\033[0m={round(config.HEIGHTMAP_LACUNARITY, 3)}"
    )

def regenerateTerrain():
    config.HEIGHTMAP_BASE_SEED = dpg.get_value("seed_input")
    config.HEIGHTMAP_SCALE = dpg.get_value("scale")
    config.HEIGHTMAP_OCTAVES = dpg.get_value("octaves")
    config.HEIGHTMAP_PERSISTENCE = dpg.get_value("persistence")
    config.HEIGHTMAP_LACUNARITY = dpg.get_value("lacunarity")
    config.STATS_TRIANGLE_COUNT = 0
    config.STATS_ITER_COUNT = 0
    
    heightmap = generateHeightmap(config.HEIGHTMAP_WIDTH, config.HEIGHTMAP_DEPTH)
    vertices, indices = generateMesh(heightmap)

    updateStatsDisplay()
    return vertices, indices

def requestTerrainRegeneration():
    if config.TERRAIN_NEEDS_UPDATE:
        config.TERRAIN_REGEN_REQ = True

def updateTerrainParameters(sender, app_data):
    param_map = {
        "seed_input": "HEIGHTMAP_BASE_SEED",
        "scale": "HEIGHTMAP_SCALE",
        "octave": "HEIGHTMAP_OCTAVES",
        "persistence": "HEIGHTMAP_PERSISTENCE",
        "lacunarity": "HEIGHTMAP_LACUNARITY"
    }
    if sender in param_map:
        setattr(config, param_map[sender], app_data)
        config.TERRAIN_NEEDS_UPDATE = True
        updateStatsDisplay()

def updateStatsDisplay():
    dpg.set_value("tri_count", f"Triangles: {config.STATS_TRIANGLE_COUNT}")
    dpg.set_value("iter_count", f"Iterations: {config.STATS_ITER_COUNT}")

def main():
    configureEnvironment()
    vertices, indices = regenerateTerrain()
    terrainParamsToLogger(True)

    clock = pygame.time.Clock()
    running = True
    while running:
        dpg.render_dearpygui_frame()
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        if config.TERRAIN_NEEDS_UPDATE and config.TERRAIN_REGEN_REQ:
            try:
                vertices, indices = regenerateTerrain()
                terrainParamsToLogger()
            except Exception as e:
                logger.error(f"Regeneration failed: {e}")
            finally:
                config.TERRAIN_NEEDS_UPDATE = False
                config.TERRAIN_REGEN_REQ = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        renderTerrain(vertices, indices)
        glPopMatrix()
        pygame.display.flip()

    cleanupEnvironment()

if __name__ == "__main__":
    main()
