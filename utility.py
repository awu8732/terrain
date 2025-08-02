import logging
import dearpygui.dearpygui as dpg
import configuration as config
import core.state as state
import numpy as np

logger = logging.getLogger("TERRAIN")

class BiomeClassifier:
    """
    Handles biome classification based on temperature and moisture values.
    
    Provides methods for determining biome types and retrieving appropriate
    colors for terrain rendering based on environmental conditions.
    """
    
    @staticmethod
    def get_biome(temperature, moisture):
        """Classify biome based on temperature and moisture levels."""
        if temperature < 0.3:
            return "TUNDRA" if moisture < 0.4 else "TAIGA"
        elif temperature > 0.7:
            if moisture < 0.2:
                return "DESERT"
            elif moisture > 0.8:
                return "RAINFOREST"
            else:
                return "SAVANNA"
        else:
            if moisture < 0.3:
                return "GRASSLAND"
            else:
                return "TEMPERATE"
    
    @staticmethod
    def get_biome_color_from_vertex(vertex, biome_map, 
                                  default_color=(128, 128, 128), 
                                  error_color=(255, 0, 0)):
        """Get the biome color for a specific vertex position."""
        x, y, z = vertex
        i = int(round(x))
        j = int(round(z))
        
        # Check bounds and retrieve biome color
        if 0 <= i < biome_map.shape[0] and 0 <= j < biome_map.shape[1]:
            biome = biome_map[i][j]
            return config.BIOME_COLORS.get(biome, default_color)
        else:
            return error_color

class CameraManager:
    """
    Manages camera positioning and view calculations for 3D terrain viewing.
    
    Provides methods for calculating optimal camera positions and view
    vectors based on terrain dimensions and elevation settings.
    """
    
    @staticmethod
    def get_camera_eye_pos(width, depth, elevation_view):
        """Positions the camera to provide a good overview of the entire
        terrain with appropriate elevation for perspective."""
        eye_x = width / 2
        eye_y = elevation_view * depth
        eye_z = depth
        return np.array([eye_x, eye_y, eye_z])
    
    @staticmethod
    def get_camera_view_vec(width, depth, elevation_view):
        """Calculate camera view direction vector."""
        eye = CameraManager.get_camera_eye_pos(width, depth, elevation_view)
        center = np.array([width / 2, 0.0, depth / 2])
        view_dir = center - eye
        return view_dir / np.linalg.norm(view_dir)

class StatisticsManager:
    """
    Manages performance statistics and erosion data tracking.
    
    Handles the collection, formatting, and display of various performance
    metrics and erosion simulation statistics.
    """
    
    @staticmethod
    def output_erosion_statistics():
        """Output erosion simulation statistics to console."""
        print(f"PARTICLES_DEPOSITED: {state.STATS.TOTAL_D}")
        print(f"PARTICLES_ERODED: {state.STATS.TOTAL_E}")
        print(f"EROSION_TIME: {round(state.STATS.ERO_TIME, 3)}ms")
    
    @staticmethod
    def reset_erosion_statistics():
        """Reset all erosion-related statistics to zero."""
        state.STATS.TOTAL_D = 0.0
        state.STATS.TOTAL_E = 0.0
        state.STATS.ERO_TIME = 0.0
    
    @staticmethod
    def terrain_params_to_logger(on_start=False):
        """Log current terrain generation parameters with color formatting."""
        message = "Regeneration successful"
        if on_start:
            message = "Initial terrain"
            
        logger.info(
            f"\033[0m{message}: \033[0m | "
            f"\033[36mSeed\033[0m: {config.HEIGHTMAP_BASE_SEED} | "
            f"\033[36mRes\033[0m: {config.HEIGHTMAP_WIDTH}x{config.HEIGHTMAP_DEPTH}|\n"
            f"    \033[33mScl\033[0m={round(config.HEIGHTMAP_SCALE, 2)} "
            f"\033[33mOct\033[0m={config.HEIGHTMAP_OCTAVES} "
            f"\033[33mPer\033[0m={round(config.HEIGHTMAP_PERSISTENCE, 3)} "
            f"\033[33mLac\033[0m={round(config.HEIGHTMAP_LACUNARITY, 3)} "
            f"\033[35mEro\033[0m={'Y' if config.SIMULATE_EROSION else 'N'} "
            f"\033[35mItr\033[0m={config.EROSION_ITERATIONS} "
            f"\033[35mVel\033[0m={round(config.EROSION_INIT_VELOCITY, 3)} "
            f"\033[32mBio\033[0m={'Y' if config.SIMULATE_BIOME else 'N'} "
            f"\033[32mMoi\033[0m={round(config.BIOME_MOISTURE, 3)} "
            f"\033[32mTmp\033[0m={round(config.BIOME_TEMPERATURE, 3)} "
        )
    
    @staticmethod
    def update_stats_display():
        """Update the DearPyGUI statistics display with current performance data."""
        # Performance Metrics
        dpg.set_value("frame_time", f"Frame Time: {state.STATS.FRAME_TIME:.1f}ms")
        dpg.set_value("fps", f"FPS: {state.STATS.FPS:.0f}")
        dpg.set_value("gen_time", f"Generation Time: {state.STATS.GEN_TIME:.1f}ms")
        dpg.set_value("render_time", f"Rendering Time: {state.STATS.RENDER_TIME:.1f}ms")
        
        # Mesh Statistics
        dpg.set_value("tri_count", f"Triangles: {state.STATS.TRIANGLE_COUNT:,}")
        dpg.set_value("vert_count", f"Vertices: {state.STATS.VERTEX_COUNT:,}")

class UtilityManager:
    """
    Main utility manager that provides a unified interface to all utility functions.
    
    Aggregates functionality from specialized utility classes and provides
    convenient access to commonly used helper functions.
    """
    
    def __init__(self):
        self.biome_classifier = BiomeClassifier()
        self.camera_manager = CameraManager()
        self.stats_manager = StatisticsManager()
    
    def get_biome(self, temperature, moisture):
        """Classify biome based on temperature and moisture."""
        return self.biome_classifier.get_biome(temperature, moisture)
    
    def get_biome_color_from_vertex(self, vertex, biome_map, 
                                  default_color=(128, 128, 128), 
                                  error_color=(255, 0, 0)):
        """Get biome color for a vertex position."""
        return self.biome_classifier.get_biome_color_from_vertex(
            vertex, biome_map, default_color, error_color
        )
    
    def get_camera_eye_pos(self, width, depth, elevation_view):
        """Calculate camera eye position."""
        return self.camera_manager.get_camera_eye_pos(width, depth, elevation_view)
    
    def get_camera_view_vec(self, width, depth, elevation_view):
        """Camera view direction vector."""
        return self.camera_manager.get_camera_view_vec(width, depth, elevation_view)
    
    def output_erosion_statistics(self):
        """Output erosion simulation statistics to console."""
        self.stats_manager.output_erosion_statistics()
    
    def reset_erosion_statistics(self):
        """Reset erosion statistics to zero."""
        self.stats_manager.reset_erosion_statistics()
    
    def terrain_params_to_logger(self, on_start=False):
        """Log terrain generation parameters."""
        self.stats_manager.terrain_params_to_logger(on_start)
    
    def update_stats_display(self):
        """Update the UI statistics display."""
        self.stats_manager.update_stats_display()

# Global UI manager instance
_utility_manager = UtilityManager()