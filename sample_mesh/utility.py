import logging
import dearpygui.dearpygui as dpg
import configuration as config
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

def outputErosionStatistics():
    print(f"PARTICLES_DEPOSITED: {config.STATS.TOTAL_D}")
    print(f"PARTICLES_ERODED: {config.STATS.TOTAL_E}")
    print(f"EROSION_TIME: {round(config.STATS.ERO_TIME,3)}ms")

def resetErosionStatistics():
    config.STATS.TOTAL_D = 0.0
    config.STATS.TOTAL_E = 0.0
    config.STATS.ERO_TIME = 0.0

def terrainParamsToLogger(onStart = False):
    message = "Regeneration successful"
    if onStart:
        message = "Initial terrain"
    logger.info(
        f"\033[0m{message}: \033[0m | "
        f"\033[36mSeed\033[0m: {config.HEIGHTMAP_BASE_SEED} | "
        f"\033[36mRes\033[0m: {config.HEIGHTMAP_WIDTH}x{config.HEIGHTMAP_DEPTH}|\n"
        f"    \033[33mScale\033[0m={round(config.HEIGHTMAP_SCALE, 2)} "
        f"\033[33mOctaves\033[0m={config.HEIGHTMAP_OCTAVES} "
        f"\033[33mPersist\033[0m={round(config.HEIGHTMAP_PERSISTENCE, 3)} "
        f"\033[33mLacun\033[0m={round(config.HEIGHTMAP_LACUNARITY, 3)} "
        f"\033[35mEro\033[0m={'Y' if config.SIMULATE_EROSION else 'N'} "
        f"\033[35mIter\033[0m={config.EROSION_ITERATIONS} "
        f"\033[35mVel\033[0m={round(config.EROSION_INIT_VELOCITY,3)} "
        f"\033[32mBiom\033[0m={'Y' if config.SIMULATE_BIOME else 'N'} "
        f"\033[32mMois\033[0m={round(config.BIOME_MOISTURE,3)} "
        f"\033[32mTmp\033[0m={round(config.BIOME_TEMPERATURE,3)} "
    )

def updateStatsDisplay():
    # Performance Metrics
    dpg.set_value("frame_time", f"Frame Time: {config.STATS.FRAME_TIME:.1f}ms")
    dpg.set_value("fps", f"FPS: {config.STATS.FPS:.0f}")
    dpg.set_value("gen_time", f"Generation Time: {config.STATS.GEN_TIME:.1f}ms")
    dpg.set_value("render_time", f"Rendering Time: {config.STATS.RENDER_TIME:.1f}ms")
    # Mesh Stats
    dpg.set_value("tri_count", f"Triangles: {config.STATS.TRIANGLE_COUNT:,}")
    dpg.set_value("vert_count", f"Vertices: {config.STATS.VERTEX_COUNT:,}")
