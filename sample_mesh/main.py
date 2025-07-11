import logging
import time
import pygame
from pygame.locals import *
import dearpygui.dearpygui as dpg
from OpenGL.GL import * 
from OpenGL.GLU import *

from mesh_generation import *
from utility import *
import configuration as config
import env_manager as env

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]  # Send to terminal
)
logger = logging.getLogger("TERRAIN")

def main():
    env.configureEnvironment()
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

    env.cleanupEnvironment()

if __name__ == "__main__":
    main()
