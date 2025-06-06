from dataclasses import dataclass
from enum import Enum


class EventStatus(Enum):
    JOB_COMES = "job_comes"
    WORKER_ENDS = "worker_ends"

    def __str__(self):
        return self.value


class Event:
    def __init__(self, machine_name: str,
                 time: int, status: EventStatus,
                 processing_start: int = -1,
                 processing_end: int = -1):
        self.machine_name: str = machine_name
        self.time: int = time
        self.status: EventStatus = status

        self.processing_start: int = processing_start
        self.processing_end: int = processing_end

    def __lt__(self, other):
        return self.time < other.time

    def __repr__(self):
        return f"machine_name={self.machine_name}, time={self.time}, status={self.status}"


@dataclass
class Job:
    produced_time: int
    duration: int
    machine_name: str

    def __repr__(self):
        return f"Job(produced_time={self.produced_time}, duration={self.duration}, machine_name={self.machine_name})"
