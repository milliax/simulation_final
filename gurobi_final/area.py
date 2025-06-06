
import heapq
from struct import Argument, Event, Work, show_iteration, show_arrival_info, show_dispatch_info
from server import Server
from collections import deque

from typing import TypedDict


class Machine(TypedDict):
    machine: str
    processing_time: int
    load_unload_time: int


class AreaDispatcher:
    def __init__(self):
        self.servers = []
        self.events = []
        self.work_todo = deque()
        self.arg = None

    def config(self, number_of_workers: int, machines: list[Machine], total_processing_time: int, area_name: str):
        # self.arg = input_arg
        # self.servers = [Server() for _ in range(self.arg.number_of_servers)]
        self.work_todo.clear()
        self.events.clear()

        self.area_name = area_name
        self.number_of_workers = number_of_workers
        self.total_processing_time = total_processing_time

        self.servers = [Server(processing_time=machine.processing_time,
                               load_unload_time=machine.load_unload_time,
                               machine_name=machine.machine)
                        for machine in machines]

    def start(self) -> float:
        heapq.heappush(self.events, Event(0, "arrival"))
        total_waiting_time = 0.0
        jobs_dispatched = 0
        num_of_iteration = 0

        available_workers = self.number_of_workers

        while self.events:
            latest_event = heapq.heappop(self.events)

            if show_iteration:
                print(f"\nIteration: {num_of_iteration}")
                print(f"statistics: ")
                print(f"number of jobs: {len(self.work_todo)}")
                print(f"number in queue: {len(self.events)}")
                print(f"number of servers: {len(self.servers)}")
                print(f"number of jobs dispatched: {jobs_dispatched}")
                print(f"this Time: {latest_event.time}")
                print(f"this Instruction: {latest_event.instruction}\n")
                num_of_iteration += 1

            if latest_event.instruction == "arrival":
                if jobs_dispatched >= self.arg.number_of_jobs:
                    continue

                jobs_dispatched += 1

                if show_arrival_info:
                    print(f"\nJob arrived at {latest_event.time}")

                # TODO: replace random with machine
                inter = self.arg.inter_arrival_start + random.random() * \
                    (self.arg.inter_arrival_end - self.arg.inter_arrival_start)
                service_time = self.arg.service_time_start + random.random() * \
                    (self.arg.service_time_end - self.arg.service_time_start)

                self.work_todo.append(Work(service_time, latest_event.time))
                heapq.heappush(self.events, Event(
                    latest_event.time + inter, "arrival"))

            elif latest_event.instruction == "job_finish":
                available_workers += 1

            else:
                print("Undefined instruction in LifetimeManager")

            if self.work_todo:
                for s in self.servers:
                    if s.available(latest_event.time):
                        work = self.work_todo.popleft()
                        if show_dispatch_info:
                            print(
                                f"Server dispatched at {latest_event.time}, with duration: {work.duration}")
                        waiting_time = s.picked(latest_event.time, work)
                        heapq.heappush(self.events, Event(
                            s.finishing_time(), "job_finish"))
                        total_waiting_time += waiting_time
                        break

        return total_waiting_time / jobs_dispatched
