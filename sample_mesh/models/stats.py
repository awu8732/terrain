class Stats:
    def __init__(self):
        self.TRIANGLE_COUNT = 0
        self.VERTEX_COUNT = 0
        self.ITER_COUNT = 0
        self.GEN_TIME = 0.0       # terrain generation time (ms)
        self.RENDER_TIME = 0.0    # GPU rendering time (ms)
        self.FRAME_TIME = 0.0     # Full frame time (ms)
        self.FPS = 0
        self.TOTAL_D = 0.0
        self.TOTAL_E = 0.0
        self.ERO_TIME = 0.0