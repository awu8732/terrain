import logging
import numpy as np
import random as rand
import pygame
from pygame.locals import *
import dearpygui.dearpygui as dpg
from OpenGL.GL import * 
from OpenGL.GLU import *

import configuration as config
from core.ui_manager import _ui_manager
import models
import core.state as state
import models.mesh
import models.stats
import utility

logger = logging.getLogger("TERRAIN")


class OpenGLManager:
    """
    Handles OpenGL context initialization and configuration.
    
    Sets up the OpenGL rendering pipeline with appropriate projection
    matrix, depth testing, and rendering states for 3D terrain visualization.
    """
    
    @staticmethod
    def initialize_gl_context(display_size):
        """
        Initialize OpenGL rendering context and set up projection matrix.
        
        Configures the OpenGL pipeline for 3D rendering with perspective
        projection, depth testing, smooth shading, and face culling.
        """
        # Set up projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(
            config.WINDOW_FOV, 
            display_size[0] / display_size[1],
            config.WINDOW_CLIPPING_NEAR, 
            config.WINDOW_CLIPPING_FAR
        )
        
        # Switch to modelview matrix for scene transformations
        glMatrixMode(GL_MODELVIEW)
        
        # Enable rendering features
        glEnable(GL_DEPTH_TEST)      # Enable depth buffering
        glShadeModel(GL_SMOOTH)      # Enable smooth shading
        glEnable(GL_CULL_FACE)       # Enable back-face culling
        
        logger.info("OpenGL context initialized successfully")


class UIManager:
    """
    Manages DearPyGUI interface initialization and viewport setup.
    
    Handles the creation and configuration of the user interface
    for terrain parameter controls and statistics display.
    """
    
    @staticmethod
    def initialize_ui_context():
        """Initialize DearPyGUI context and create the control interface."""
        dpg.create_context()
        _ui_manager.initialize_terrain_controls()
        dpg.create_viewport(
            title="TERRAIN CONTROLS", 
            width=400, 
            height=600
        )
        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        logger.info("DearPyGUI interface initialized successfully")


class StateManager:
    """
    Manages global application state initialization.
    
    Handles the setup of global state variables, mesh objects,
    statistics tracking, and lighting configuration.
    """
    
    @staticmethod
    def initialize_application_state():
        """Initialize global application state and create core objects."""
        # Initialize random seed for terrain generation
        config.HEIGHTMAP_BASE_SEED = rand.randint(1, 500)
        state.STATS = models.stats.Stats()
        state.MESH = models.mesh.Mesh()

        StateManager._configure_lighting()
        logger.info("Application state initialized successfully")
    
    @staticmethod
    def _configure_lighting():
        """Configure lighting parameters for terrain rendering."""
        # Normalize light direction vector
        light_dir = np.array(config.LIGHTING_L_DIR)
        config.LIGHTING_L_DIR = light_dir / np.linalg.norm(light_dir)
        
        # Calculate camera view vector for lighting
        utility_manager = utility.UtilityManager()
        config.LIGHTING_V_DIR = utility_manager.get_camera_view_vec(
            config.HEIGHTMAP_WIDTH, 
            config.HEIGHTMAP_DEPTH, 
            config.ELEVATION_VIEW
        )
        
        logger.info("Lighting configuration complete")


class EnvironmentManager:
    """
    Main environment manager coordinating all initialization tasks.
    
    Provides a unified interface for setting up the complete application
    environment including pygame, OpenGL, UI, and application state.
    """
    
    def __init__(self):
        self.opengl_manager = OpenGLManager()
        self.ui_manager = UIManager()
        self.state_manager = StateManager()
    
    def configure_environment(self):
        """Configure the complete application environment."""
        logger.info("Beginning environment configuration...")
        
        # Initialize pygame and create OpenGL context
        pygame.init()
        display_size = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        pygame.display.set_mode(display_size, DOUBLEBUF | OPENGL) # pyright: ignore[reportUndefinedVariable]
        
        # Initialize application components
        self.state_manager.initialize_application_state()
        self.opengl_manager.initialize_gl_context(display_size)
        self.ui_manager.initialize_ui_context()
        
        logger.info("Environment configuration complete")
    
    def cleanup_environment(self):
        """Clean up application resources and shut down gracefully."""
        logger.info("Cleaning up environment resources...")
        dpg.destroy_context()
        pygame.quit()
        logger.info("Environment cleanup complete")


# Global environment manager instance
_environment_manager = EnvironmentManager()
