import logging
import time
import pygame
from pygame.locals import *
import dearpygui.dearpygui as dpg
from OpenGL.GL import * 
from OpenGL.GLU import *

import configuration as config
import core.env_manager as env
from core.terrain_generation import *
import core.state as state
from utility import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]  # Send to terminal
)
logger = logging.getLogger("TERRAIN")

def main():
    env.configureEnvironment()
    normals, biome_map = regenerateTerrain()
    terrainParamsToLogger(True)

    running = True
    frame_times = []
    while running:
        frame_start = time.perf_counter()

        dpg.render_dearpygui_frame()
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        if state.TERRAIN_NEEDS_UPDATE and state.TERRAIN_REGEN_REQ:
            try:
                normals, biome_map = regenerateTerrain()
                terrainParamsToLogger()
            except Exception as e:
                logger.error(f"Regeneration failed: {e}")
            finally:
                state.TERRAIN_NEEDS_UPDATE = False
                state.TERRAIN_REGEN_REQ = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        render_start = time.perf_counter()
        glPushMatrix()
        renderTerrain(normals, biome_map)
        glPopMatrix()
        
        #stats timing
        state.STATS.RENDER_TIME = (time.perf_counter() - render_start) * 1000
        state.STATS.FRAME_TIME = (time.perf_counter() - frame_start) * 1000

        frame_times.append(state.STATS.FRAME_TIME)
        if len(frame_times) > 60:
            frame_times.pop(0)
        state.STATS.FPS = 1000 / (sum(frame_times) / len(frame_times))

        updateStatsDisplay()
        pygame.display.flip()

    env.cleanupEnvironment()

if __name__ == "__main__":
    main()
