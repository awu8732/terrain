import logging
import dearpygui.dearpygui as dpg
import configuration as config

logger = logging.getLogger("TERRAIN")

# bilinear interpolatin for smooth gradients
def calculateGradient(hmap, x, y, x_int, y_int):
    xf, yf = x - x_int, y - y_int
    h00 = hmap[x_int, y_int]
    h10 = hmap[x_int+1, y_int]
    h01 = hmap[x_int, y_int+1]
    h11 = hmap[x_int+1, y_int+1]

    dx = (h10 - h00) * (1 - yf) + (h11 - h01) * yf
    dy = (h01 - h00) * (1 - xf) + (h11 - h10) * xf
    return dx, dy

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
        f"\033[33mLacun\033[0m={round(config.HEIGHTMAP_LACUNARITY, 3)}"
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
