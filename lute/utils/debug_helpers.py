"Debug helpers."

import time


class DebugTimer:
    """
    Helper to log time.
    """

    def __init__(self, name):
        self.start = time.process_time()
        self.curr_start = self.start
        self.name = name
        self.step_map = {}
        print(f"{name} timer started")

    def step(self, s):
        "Dump time spent in step, total time since start."
        n = time.process_time()
        step_elapsed = n - self.curr_start
        total_step_elapsed = self.step_map.get(s, 0)
        total_step_elapsed += step_elapsed
        self.step_map[s] = total_step_elapsed
        total_elapsed = n - self.start
        msg = " ".join(
            [
                f"{self.name} {s}:",
                f"step_elapsed: {step_elapsed:.6f},",
                f"total step_elapsed: {total_step_elapsed:.6f},",
                f"total_elapsed: {total_elapsed:.6f}",
            ]
        )
        print(msg, flush=True)
        self.curr_start = n

    def summary(self):
        "Print final step summary."
        print(f"{self.name} summary ------------------")
        for k, v in self.step_map.items():
            print(f"  {k}: {v:.6f}", flush=True)
        print(f"end {self.name} summary --------------")
