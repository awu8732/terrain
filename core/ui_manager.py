import logging
import dearpygui.dearpygui as dpg
import configuration as config
import core.state as state

logger = logging.getLogger("TERRAIN")


class TerrainControlPanel:
    """
    Manages the terrain parameter control panel interface.
    
    Creates and handles all user interface controls for terrain generation
    parameters including heightmap settings, erosion controls, biome
    configuration, and lighting parameters.
    """
    
    def __init__(self):
        self.window_width = 400
        self.window_height = 350
        self.window_pos = (0, 0)
    
    def create_heightmap_controls(self):
        """Create UI controls for heightmap generation parameters."""
        dpg.add_input_int(
            label="Base Seed",
            default_value=config.HEIGHTMAP_BASE_SEED,
            tag="seed_input",
            callback=self._update_terrain_parameters
        )
        
        dpg.add_slider_int(
            label="Resolution",
            default_value=config.HEIGHTMAP_WIDTH, 
            min_value=50, 
            max_value=200, 
            tag="resolution",
            callback=self._update_terrain_parameters
        )
        
        dpg.add_slider_float(
            label="Height Scale",
            default_value=config.HEIGHTMAP_SCALE, 
            min_value=0.1, 
            max_value=15.0, 
            tag="scale",
            callback=self._update_terrain_parameters
        )
        
        dpg.add_slider_int(
            label="Octaves",
            default_value=config.HEIGHTMAP_OCTAVES, 
            min_value=1, 
            max_value=20, 
            tag="octaves",
            callback=self._update_terrain_parameters
        )
        
        dpg.add_slider_float(
            label="Persistence",
            default_value=config.HEIGHTMAP_PERSISTENCE, 
            min_value=0.1, 
            max_value=1.0, 
            tag="persistence",
            callback=self._update_terrain_parameters
        )
        
        dpg.add_slider_float(
            label="Lacunarity",
            default_value=config.HEIGHTMAP_LACUNARITY, 
            min_value=1.0, 
            max_value=4.0, 
            tag="lacunarity",
            callback=self._update_terrain_parameters
        )
    
    def create_erosion_controls(self):
        """Create UI controls for hydraulic erosion simulation parameters."""
        dpg.add_checkbox(
            label="Enable Hydraulic Erosion",
            default_value=config.SIMULATE_EROSION,
            tag="hydraulic_erosion",
            callback=self._update_terrain_parameters
        )
        
        dpg.add_slider_int(
            label="ITERATIONS",
            default_value=config.EROSION_ITERATIONS, 
            min_value=10000, 
            max_value=1000000, 
            tag="iterations",
            callback=self._update_terrain_parameters
        )
        
        dpg.add_slider_float(
            label="INIT VELOCITY",
            default_value=config.EROSION_INIT_VELOCITY, 
            min_value=0.0, 
            max_value=3.0, 
            tag="init_velocity",
            callback=self._update_terrain_parameters
        )
    
    def create_biome_controls(self):
        """Create UI controls for biome system parameters."""
        dpg.add_checkbox(
            label="Enable Biome",
            default_value=config.SIMULATE_BIOME,
            tag="biome",
            callback=self._update_terrain_parameters
        )
        
        dpg.add_slider_float(
            label="TEMPERATURE",
            default_value=config.BIOME_TEMPERATURE, 
            min_value=0.0, 
            max_value=1.0, 
            tag="temperature",
            callback=self._update_terrain_parameters
        )
        
        dpg.add_slider_float(
            label="MOISTURE",
            default_value=config.BIOME_MOISTURE, 
            min_value=0.0, 
            max_value=1.0, 
            tag="moisture",
            callback=self._update_terrain_parameters
        )
    
    def create_lighting_controls(self):
        """Create UI controls for Blinn-Phong lighting parameters."""
        dpg.add_slider_float(
            label="AMBIENT REF",
            default_value=config.LIGHTING_K_AMB, 
            min_value=0.0, 
            max_value=0.2, 
            tag="ambient",
            callback=self._update_terrain_parameters
        )
        
        dpg.add_slider_float(
            label="DIFFUSE REF",
            default_value=config.LIGHTING_K_DIFF, 
            min_value=0.0, 
            max_value=1.0, 
            tag="diffuse",
            callback=self._update_terrain_parameters
        )
        
        dpg.add_slider_float(
            label="SPEC REF",
            default_value=config.LIGHTING_K_SPEC, 
            min_value=0.0, 
            max_value=1.0, 
            tag="specular",
            callback=self._update_terrain_parameters
        )
        
        dpg.add_slider_int(
            label="SHININESS",
            default_value=config.LIGHTING_SHIN, 
            min_value=8, 
            max_value=128, 
            tag="shininess",
            callback=self._update_terrain_parameters
        )
    
    def create_panel(self):
        """Create the complete terrain control panel window."""
        with dpg.window(
            label="Terrain Parameters", 
            width=self.window_width, 
            height=self.window_height, 
            pos=self.window_pos,
            no_close=True, 
            no_collapse=True, 
            no_move=True
        ):
            self.create_heightmap_controls()
            self.create_erosion_controls()
            self.create_biome_controls()
            self.create_lighting_controls()
            
            dpg.add_button(
                label="REGENERATE", 
                callback=self._request_terrain_regeneration
            )
    
    def _update_terrain_parameters(self, sender, app_data):
        """Handle parameter updates from UI controls."""
        # Map UI control tags to configuration parameter names
        param_map = {
            "seed_input": "HEIGHTMAP_BASE_SEED",
            "resolution": "HEIGHTMAP_DEPTH",
            "scale": "HEIGHTMAP_SCALE",
            "octaves": "HEIGHTMAP_OCTAVES",
            "persistence": "HEIGHTMAP_PERSISTENCE",
            "lacunarity": "HEIGHTMAP_LACUNARITY",
            "hydraulic_erosion": "SIMULATE_EROSION",
            "iterations": "EROSION_ITERATIONS",
            "init_velocity": "EROSION_INIT_VELOCITY",
            "biome": "SIMULATE_BIOME",
            "temperature": "BIOME_TEMPERATURE",
            "moisture": "BIOME_MOISTURE",
            "ambient": "LIGHTING_K_AMB",
            "diffuse": "LIGHTING_K_DIFF",
            "specular": "LIGHTING_K_SPEC",
            "shininess": "LIGHTING_SHIN"
        }
        
        # Special handling for iteration count (snap to increments)
        if sender == "iterations":
            step_size = 10000
            snapped_value = round(app_data / step_size) * step_size
            dpg.set_value("iterations", snapped_value)
            setattr(config, param_map[sender], snapped_value)
            state.TERRAIN_NEEDS_UPDATE = True
        elif sender in param_map:
            # Handle resolution parameter (affects both width and depth)
            if sender == "resolution":
                setattr(config, "HEIGHTMAP_WIDTH", app_data)
                setattr(config, "HEIGHTMAP_DEPTH", app_data)
            else:
                setattr(config, param_map[sender], app_data)
            state.TERRAIN_NEEDS_UPDATE = True
    
    def _request_terrain_regeneration(self):
        """Handle regeneration button click."""
        if state.TERRAIN_NEEDS_UPDATE:
            state.TERRAIN_REGEN_REQ = True


class StatisticsPanel:
    """
    Manages the performance statistics display panel.
    
    Creates and maintains the UI display for performance metrics
    including frame rate, generation time, mesh statistics, and
    rendering performance data.
    """
    
    def __init__(self):
        self.window_width = 400
        self.window_height = 280
        self.window_pos = (0, 360)
    
    def create_panel(self):
        """Create the statistics display panel window."""
        with dpg.window(
            label="Terrain Stats", 
            width=self.window_width, 
            height=self.window_height, 
            pos=self.window_pos,
            no_close=True, 
            no_collapse=True, 
            no_move=True
        ):
            # Mesh statistics
            dpg.add_text(
                f"Triangles: {state.STATS.TRIANGLE_COUNT}", 
                tag="tri_count"
            )
            dpg.add_text(
                f"Vertices: {state.STATS.VERTEX_COUNT}", 
                tag="vert_count"
            )
            
            # Performance timing
            dpg.add_text(
                f"Generation Time: {state.STATS.GEN_TIME}", 
                tag="gen_time"
            )
            dpg.add_text(
                f"Rendering Time: {state.STATS.RENDER_TIME}", 
                tag="render_time"
            )
            
            # Real-time performance
            dpg.add_text(
                f"Frame Time: {state.STATS.FRAME_TIME}", 
                tag="frame_time"
            )
            dpg.add_text(
                f"FPS: {state.STATS.FPS}", 
                tag="fps"
            )


class UIManager:
    """
    Main UI manager coordinating all interface components.
    
    Provides a unified interface for creating and managing all
    UI panels and handles the overall interface layout.
    """
    
    def __init__(self):
        self.control_panel = TerrainControlPanel()
        self.stats_panel = StatisticsPanel()
    
    def initialize_terrain_controls(self):
        """Initialize the complete terrain control interface."""
        logger.info("Initializing terrain control panel...")
        
        self.control_panel.create_panel()
        self.stats_panel.create_panel()
        
        logger.info("Terrain control interface initialized successfully")


# Global UI manager instance
_ui_manager = UIManager()
