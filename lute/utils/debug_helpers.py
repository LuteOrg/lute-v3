"Debug helpers."

import time


class DebugTimer:
    """
    Helper to log time.
    """

    global_step_map = {}

    def __init__(self, name, display=True):
        self.start = time.process_time()
        self.curr_start = self.start
        self.name = name
        self.step_map = {}
        self.display = display
        print(f"{name} timer started")

    def step(self, s):
        "Dump time spent in step, total time since start."
        n = time.process_time()
        step_elapsed = n - self.curr_start
        total_step_elapsed = self.step_map.get(s, 0)
        total_step_elapsed += step_elapsed
        self.step_map[s] = total_step_elapsed

        if s != "":
            full_step_map_string = f"{self.name} {s}"
            global_step_elapsed = DebugTimer.global_step_map.get(
                full_step_map_string, 0
            )
            global_step_elapsed += step_elapsed
            DebugTimer.global_step_map[full_step_map_string] = global_step_elapsed

        total_elapsed = n - self.start
        self.curr_start = n

        if not self.display:
            return

        msg = " ".join(
            [
                f"{self.name} {s}:",
                f"step_elapsed: {step_elapsed:.6f},",
                f"total step_elapsed: {total_step_elapsed:.6f},",
                f"total_elapsed: {total_elapsed:.6f}",
            ]
        )
        print(msg, flush=True)

    def summary(self):
        "Print final step summary."
        print(f"{self.name} summary ------------------")
        for k, v in self.step_map.items():
            print(f"  {k}: {v:.6f}", flush=True)
        print(f"end {self.name} summary --------------")

    @classmethod
    def clear_total_summary(cls):
        cls.global_step_map = {}

    @classmethod
    def total_summary(cls):
        "Print final step summary."
        print("global summary ------------------")
        for k, v in cls.global_step_map.items():
            print(f"  {k}: {v:.6f}", flush=True)
        print("end global summary --------------")
