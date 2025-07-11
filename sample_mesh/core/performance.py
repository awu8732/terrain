import time

class PerformanceTimer:
    def __init__(self):
        self._start = 0
        self._lap = 0
    
    def start(self):
        self._start = time.perf_counter()
        self._lap = self._start

    def lap(self):
        now = time.perf_counter()
        duration  = (now - self._lap) * 1000
        self._lap = now
        return duration
    
    def total(self):
        return (time.perf_counter() - self._start) * 1000