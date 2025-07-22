import logging
import numpy as np
import random as rand
import pygame
from pygame.locals import *
import dearpygui.dearpygui as dpg
from OpenGL.GL import * 
from OpenGL.GLU import *

import configuration as config
import core.ui_manager as ui
import models
import core.state as state
import models.mesh
import models.stats
import utility

logger = logging.getLogger("TERRAIN")

def configureEnvironment():
    pygame.init()
    display = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    setupStateVariables()

    initializeGl(display)
    initializeDpg()
    logger.info("Environment configuration complete")

def initializeDpg():
    dpg.create_context()
    ui.initializeTerrainControls()
    dpg.create_viewport(title = "TERRAIN CONTROLS", width = 400, height = 600)
    dpg.setup_dearpygui()
    dpg.show_viewport()

def initializeGl(display):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(config.WINDOW_FOV, display[0]/display[1],
                  config.WINDOW_CLIPPING_NEAR, config.WINDOW_CLIPPING_FAR)
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)

def setupStateVariables():
    config.HEIGHTMAP_BASE_SEED = rand.randint(1, 500)
    state.STATS = models.stats.Stats()
    state.MESH = models.mesh.Mesh()
    configureLighting()

def cleanupEnvironment():
    dpg.destroy_context()
    pygame.quit()

def configureLighting():
    light_dir = np.array(config.LIGHTING_L_DIR)
    config.LIGHTING_L_DIR = light_dir / np.linalg.norm(light_dir)
    config.LIGHTING_V_DIR = utility.getCameraViewVec(config.HEIGHTMAP_WIDTH, 
                                                     config.HEIGHTMAP_DEPTH, 
                                                     config.ELEVATION_VIEW)