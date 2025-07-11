import logging
import random as rand
import pygame
from pygame.locals import *
import dearpygui.dearpygui as dpg
from OpenGL.GL import * 
from OpenGL.GLU import *

import configuration as config
import core.ui_manager as ui

logger = logging.getLogger("TERRAIN")

def configureEnvironment():
    pygame.init()
    display = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
    
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    config.HEIGHTMAP_BASE_SEED = rand.randint(1, 500)

    #initialize OpenGL and DearPy
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(config.WINDOW_FOV, display[0]/display[1],
                  config.WINDOW_CLIPPING_NEAR, config.WINDOW_CLIPPING_FAR)
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)

    dpg.create_context()
    ui.initializeTerrainControls()
    dpg.create_viewport(title = "TERRAIN CONTROLS", width = 400, height = 520)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    logger.info("Environment configuration complete")

def cleanupEnvironment():
    dpg.destroy_context()
    pygame.quit()