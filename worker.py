class Worker:
    working_start = -1
    working_end = -1

    # def __init__(self):
    #     self.task_queue = []
    
    def available(self, time: int) -> bool:
        if time + 1e-6 < self.working_end:
            return False
        self.working_start = -1
        self.working_end = -1
        return True

    def picked(self, time: int, work_duration: int) -> int:
        self.working_start = time
        self.working_end = time + work_duration

        return self.working_end