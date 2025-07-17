import logging
import dearpygui.dearpygui as dpg
import configuration as config

logger = logging.getLogger("TERRAIN")

def initializeTerrainControls():
    logger.info("Initializing terrain control panel..")
    with dpg.window(label = "Terrain Parameters", width = 400, height = 240, pos = (0,0),
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
                             max_value = 15.0, 
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
        dpg.add_checkbox(label="Enable Hydraulic Erosion",
                     default_value=config.SIMULATE_EROSION,
                     tag="hydraulic_erosion",
                     callback=updateTerrainParameters)
        dpg.add_slider_int(label = "ITERATIONS",
                             default_value = config.EROSION_ITERATIONS, 
                             min_value = 10000, 
                             max_value = 1e6, 
                             tag = "iterations",
                             callback = updateTerrainParameters)
        
        dpg.add_button(label = "REGNERATE", callback = requestTerrainRegeneration)

    with dpg.window(label = "Terrain Stats", width = 400, height = 300, pos = (0, 250),
                    no_close = True, no_collapse = True, no_move = True):
        dpg.add_text(f"Triangles: {config.STATS.TRIANGLE_COUNT}", tag="tri_count")
        dpg.add_text(f"Vertices: {config.STATS.VERTEX_COUNT}", tag="vert_count")

        dpg.add_text(f"Generation Time: {config.STATS.GEN_TIME}", tag="gen_time")
        dpg.add_text(f"Rendering Time: {config.STATS.RENDER_TIME}", tag="render_time")

        dpg.add_text(f"Frame Time: {config.STATS.FRAME_TIME}", tag="frame_time")
        dpg.add_text(f"FPS: {config.STATS.FPS}", tag="fps")

def requestTerrainRegeneration():
    if config.TERRAIN_NEEDS_UPDATE:
        config.TERRAIN_REGEN_REQ = True

def updateTerrainParameters(sender, app_data):
    param_map = {
        "seed_input": "HEIGHTMAP_BASE_SEED",
        "resolution": "HEIGHTMAP_DEPTH",
        "scale": "HEIGHTMAP_SCALE",
        "octaves": "HEIGHTMAP_OCTAVES",
        "persistence": "HEIGHTMAP_PERSISTENCE",
        "lacunarity": "HEIGHTMAP_LACUNARITY",
        "hydraulic_erosion": "SIMULATE_EROSION",
        "iterations": "EROSION_ITERATIONS"
    }
    if sender == "iterations":
        STEP_SIZE = 10000
        snapped_value = round(app_data / STEP_SIZE) * STEP_SIZE
        dpg.set_value("iterations", snapped_value)
        setattr(config, param_map[sender], snapped_value)
    elif sender in param_map:
        setattr(config, param_map[sender], app_data)
        config.TERRAIN_NEEDS_UPDATE = True