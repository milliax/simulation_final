from dataclasses import dataclass

@dataclass
class Argument:
    inter_arrival_start: int
    inter_arrival_end: int
    service_time_start: int
    service_time_end: int
    number_of_jobs: int
    number_of_servers: int


@dataclass(order=True)
class Event:
    time: float
    instruction: str = field(compare=False)


@dataclass
class Work:
    duration: float
    produced_time: float
