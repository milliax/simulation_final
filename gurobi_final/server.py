from struct import Work


class Server:
    def __init__(self, processing_time: int, load_unload_time: int,machine_name: str):
        self.processing_from = -1
        self.processing_to = -1

        self.processing_time = processing_time
        self.load_unload_time = load_unload_time
        self.machine_name = machine_name

    def available(self, now_time: float) -> bool:
        if now_time + 1e-6 < self.processing_to:
            return False
        self.processing_from = -1
        self.processing_to = -1

        return True

    def picked(self, now_time: float, work_selected: Work) -> float:
        waiting_time = now_time - work_selected.produced_time
        self.processing_from = now_time
        self.processing_to = now_time + work_selected.duration
        return waiting_time

    def finishing_time(self) -> float:
        return self.processing_to
