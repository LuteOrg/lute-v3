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
        print(f"{name} timer started")

    def step(self, s):
        "Dump time spent in step, total time since start."
        n = time.process_time()
        step_elapsed = n - self.curr_start
        total_elapsed = n - self.start
        msg = " ".join(
            [
                f"{self.name} {s}:",
                f"step_elapsed: {step_elapsed},",
                f"total_elapsed: {total_elapsed}",
            ]
        )
        print(msg, flush=True)
        self.curr_start = n
