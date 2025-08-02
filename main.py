import logging
import time
import pygame
from pygame.locals import *
import dearpygui.dearpygui as dpg
from OpenGL.GL import * 
from OpenGL.GLU import *

import configuration as config
from core.env_manager import _environment_manager
from core.terrain_generation import TerrainRenderer
import core.state as state
from utility import UtilityManager

# Configure logging for the application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("TERRAIN")


class TerrainApplication:
    """Manages the application lifecycle, rendering loop, and user interface
    interactions for real-time terrain generation and visualization."""
    
    def __init__(self):
        self.running = True
        self.frame_times = []
        self.terrain_renderer = TerrainRenderer()
        self.utility_manager = UtilityManager()
        self.normals = None
        self.biome_map = None
        
    def initialize(self):
        """
        Initialize the application environment and generate initial terrain.
        
        Sets up OpenGL context, DearPyGUI interface, and creates the first
        terrain with default parameters.
        """
        logger.info("Initializing terrain generation application...")
        _environment_manager.configure_environment()
        self.normals, self.biome_map = self.terrain_renderer.regenerate_terrain()
        self.utility_manager.terrain_params_to_logger(on_start=True)
        logger.info("Application initialization complete")
        
    def handle_events(self):
        """Process pygame events and check for application termination."""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                return False
        return True
        
    def update_terrain_if_needed(self):
        """Regenerate terrain if user has requested updates through the UI."""
        if state.TERRAIN_NEEDS_UPDATE and state.TERRAIN_REGEN_REQ:
            try:
                logger.info("Regenerating terrain with new parameters...")
                self.normals, self.biome_map = self.terrain_renderer.regenerate_terrain()
                self.utility_manager.terrain_params_to_logger(on_start=False)
            except Exception as e:
                logger.error(f"Terrain regeneration failed: {e}")
            finally:
                state.TERRAIN_NEEDS_UPDATE = False
                state.TERRAIN_REGEN_REQ = False
                
    def render_frame(self):
        """Render a single frame of the terrain visualization."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        render_start = time.perf_counter()
        glPushMatrix()
        self.terrain_renderer.render_terrain(self.normals, self.biome_map)
        glPopMatrix()
        
        # Update rendering performance statistics
        state.STATS.RENDER_TIME = (time.perf_counter() - render_start) * 1000
        
    def update_performance_stats(self, frame_start_time):
        """Update frame timing and FPS statistics."""
        state.STATS.FRAME_TIME = (time.perf_counter() - frame_start_time) * 1000
        
        # Maintain rolling average of frame times for smooth FPS calculation
        self.frame_times.append(state.STATS.FRAME_TIME)
        if len(self.frame_times) > 60:  # Keep last 60 frames
            self.frame_times.pop(0)
            
        # Calculate FPS from average frame time
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        state.STATS.FPS = 1000 / avg_frame_time if avg_frame_time > 0 else 0

        self.utility_manager.update_stats_display()
        
    def run(self):
        """Execute the main application loop."""
        logger.info("Starting main application loop...")
        
        while self.running:
            frame_start = time.perf_counter()
            dpg.render_dearpygui_frame()
            
            # Process events and check for exit
            if not self.handle_events():
                break
                
            # Update terrain if parameters changed
            self.update_terrain_if_needed()
            
            # Render 3D scene
            self.render_frame()
            
            # Update performance metrics
            self.update_performance_stats(frame_start)
            pygame.display.flip()
            
        logger.info("Application loop terminated")
        
    def cleanup(self):
        """Clean up resources and terminate the application gracefully."""
        logger.info("Cleaning up application resources...")
        _environment_manager.cleanup_environment()
        logger.info("Application shutdown complete")


def main():
    """ Application entry point. """
    app = TerrainApplication()
    
    try:
        app.initialize()
        app.run()
    except Exception as e:
        logger.error(f"Unhandled application error: {e}")
        raise
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()