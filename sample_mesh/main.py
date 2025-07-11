import dearpygui.dearpygui as dpg
import logging
from OpenGL.GL import * 
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import random as rand
import time

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
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(config.WINDOW_FOV, display[0]/display[1],
                  config.WINDOW_CLIPPING_NEAR, config.WINDOW_CLIPPING_FAR)
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)

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
    with dpg.window(label = "Terrain Parameters", width = 400, height = 200, pos = (0,0),
                    no_close = True, no_collapse = True, no_move = True):
        dpg.add_input_int(label = "Base Seed",
                             default_value = config.HEIGHTMAP_BASE_SEED,
                             tag = "seed_input",
                             callback = updateTerrainParameters)
        dpg.add_slider_int(label = "Resolution",
                             default_value = config.HEIGHTMAP_WIDTH, 
                             min_value = 50, 
                             max_value = 200, 
                             tag = "resolution",
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

    with dpg.window(label = "Terrain Stats", width = 400, height = 300, pos = (0, 210),
                    no_close = True, no_collapse = True, no_move = True):
        dpg.add_text(f"Triangles: {config.STATS.TRIANGLE_COUNT}", tag="tri_count")
        dpg.add_text(f"Vertices: {config.STATS.VERTEX_COUNT}", tag="vert_count")
        #dpg.add_text(f"Iterations: {config.STATS.ITER_COUNT}", tag="iter_count")

        dpg.add_text(f"Generation Time: {config.STATS.GEN_TIME}", tag="gen_time")
        dpg.add_text(f"Rendering Time: {config.STATS.RENDER_TIME}", tag="render_time")

        dpg.add_text(f"Frame Time: {config.STATS.FRAME_TIME}", tag="frame_time")
        dpg.add_text(f"FPS: {config.STATS.FPS}", tag="fps")

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
    gen_start = time.perf_counter()
    heightmap = generateHeightmap()
    vertices, indices = generateMesh(heightmap)
    config.STATS.VERTEX_COUNT = len(vertices)
    config.STATS.TRIANGLE_COUNT = len(indices) // 3
    config.STATS.GEN_TIME = (time.perf_counter() - gen_start) * 1000
    updateStatsDisplay()

    #reset opengl view
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(-1 * config.HEIGHTMAP_WIDTH / 2, -10, -1 * config.HEIGHTMAP_DEPTH)
    return vertices, indices

def requestTerrainRegeneration():
    if config.TERRAIN_NEEDS_UPDATE:
        config.TERRAIN_REGEN_REQ = True

def updateTerrainParameters(sender, app_data):
    param_map = {
        "seed_input": "HEIGHTMAP_BASE_SEED",
        "resolution": "HEIGHTMAP_WIDTH",
        "resolution": "HEIGHTMAP_DEPTH",
        "scale": "HEIGHTMAP_SCALE",
        "octave": "HEIGHTMAP_OCTAVES",
        "persistence": "HEIGHTMAP_PERSISTENCE",
        "lacunarity": "HEIGHTMAP_LACUNARITY"
    }
    if sender in param_map:
        setattr(config, param_map[sender], app_data)
        config.TERRAIN_NEEDS_UPDATE = True

def updateStatsDisplay():
    # Performance Metrics
    dpg.set_value("frame_time", f"Frame Time: {config.STATS.FRAME_TIME:.1f}ms")
    dpg.set_value("fps", f"FPS: {config.STATS.FPS:.0f}")
    dpg.set_value("gen_time", f"Generation Time: {config.STATS.GEN_TIME:.1f}ms")
    dpg.set_value("render_time", f"Rendering Time: {config.STATS.RENDER_TIME:.1f}ms")
    # Mesh Stats
    dpg.set_value("tri_count", f"Triangles: {config.STATS.TRIANGLE_COUNT:,}")
    dpg.set_value("vert_count", f"Vertices: {config.STATS.VERTEX_COUNT:,}")

def main():
    configureEnvironment()
    vertices, indices = regenerateTerrain()
    terrainParamsToLogger(True)

    running = True
    frame_times = []
    while running:
        frame_start = time.perf_counter()

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
        render_start = time.perf_counter()
        glPushMatrix()
        renderTerrain(vertices, indices)
        glPopMatrix()
        
        #stats timing
        config.STATS.RENDER_TIME = (time.perf_counter() - render_start) * 1000
        config.STATS.FRAME_TIME = (time.perf_counter() - frame_start) * 1000

        frame_times.append(config.STATS.FRAME_TIME)
        if len(frame_times) > 60:
            frame_times.pop(0)
        config.STATS.FPS = 1000 / (sum(frame_times) / len(frame_times))

        updateStatsDisplay()
        pygame.display.flip()

    cleanupEnvironment()

if __name__ == "__main__":
    main()
