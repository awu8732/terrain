import logging
import dearpygui.dearpygui as dpg
import configuration as config
import core.state as state
import numpy as np

logger = logging.getLogger("TERRAIN")

def getBiome(temperature, moisture):
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

def getBiomeColorFromVertex(vertex, biome_map, 
                            default_color=(128, 128, 128), 
                            error_color=(255, 0, 0)):
    x, y, z = vertex
    i = int(round(x))
    j = int(round(z))

    if 0 <= i < biome_map.shape[0] and 0 <= j < biome_map.shape[1]:
        biome = biome_map[i][j]
        return config.BIOME_COLORS.get(biome, default_color)
    else:
        return error_color
    
def getCameraEyePos(width, depth, elevation_view):
    eye_x = width / 2
    eye_y = elevation_view * depth
    eye_z = depth
    return np.array([eye_x, eye_y, eye_z])

def getCameraViewVec(width, depth, elevation_view):
    eye = getCameraEyePos(width, depth, elevation_view)
    center = np.array([width / 2, 0.0, depth / 2])
    view_dir = center - eye
    return view_dir / np.linalg.norm(view_dir)

def outputErosionStatistics():
    print(f"PARTICLES_DEPOSITED: {state.STATS.TOTAL_D}")
    print(f"PARTICLES_ERODED: {state.STATS.TOTAL_E}")
    print(f"EROSION_TIME: {round(state.STATS.ERO_TIME,3)}ms")

def resetErosionStatistics():
    state.STATS.TOTAL_D = 0.0
    state.STATS.TOTAL_E = 0.0
    state.STATS.ERO_TIME = 0.0

def terrainParamsToLogger(onStart = False):
    message = "Regeneration successful"
    if onStart:
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
        f"\033[35mVel\033[0m={round(config.EROSION_INIT_VELOCITY,3)} "
        f"\033[32mBio\033[0m={'Y' if config.SIMULATE_BIOME else 'N'} "
        f"\033[32mMoi\033[0m={round(config.BIOME_MOISTURE,3)} "
        f"\033[32mTmp\033[0m={round(config.BIOME_TEMPERATURE,3)} "
    )

def updateStatsDisplay():
    # Performance Metrics
    dpg.set_value("frame_time", f"Frame Time: {state.STATS.FRAME_TIME:.1f}ms")
    dpg.set_value("fps", f"FPS: {state.STATS.FPS:.0f}")
    dpg.set_value("gen_time", f"Generation Time: {state.STATS.GEN_TIME:.1f}ms")
    dpg.set_value("render_time", f"Rendering Time: {state.STATS.RENDER_TIME:.1f}ms")
    # Mesh Stats
    dpg.set_value("tri_count", f"Triangles: {state.STATS.TRIANGLE_COUNT:,}")
    dpg.set_value("vert_count", f"Vertices: {state.STATS.VERTEX_COUNT:,}")
