import os
import heapq

from type import Event, Job, EventStatus
from worker import Worker

from dotenv import load_dotenv
load_dotenv()


class AreaDispatcher:
    # jobs is a Job heap queue
    # events = heapq.heapify([])
    events: list[Event] = []
    job_queue: list[Job] = []

    def __init__(self, number_of_workers, machines, total_processing_time, area_name):
        self.number_of_workers = number_of_workers
        self.machines = machines
        self.total_processing_time = total_processing_time
        self.area_name = area_name

        self.events: list[Event] = []
        self.job_queue: list[Job] = []
        
        # write data with filename {area_name}-{number_of_workers}-{total_processing_time}.csv
        self.foldername = "results"
        self.filename = f"{area_name}-{number_of_workers}-{total_processing_time}.csv"

        self.file = open(f"results/{self.filename}", "w")
        # clear the data
        self.file.truncate(0)
        # write the header
        self.file.write("Machine,Processing Start,Processing End,Loading Start,Loading End\n")

    def dispatch(self) -> int:
        # Placeholder for dispatch logic
        isDebug = os.getenv("DEBUG") == "true"

        if (isDebug):
            print(
                f"Dispatching for area: {self.area_name} with {self.number_of_workers} workers")
        # Here you would implement the actual dispatch logic

        # print(f"Machines: {self.machines}")

        available_workers = [Worker() for _ in range(self.number_of_workers)]

        total_waiting_time = 0

        process_end: dict[str, int] = {}

        for machine in self.machines:
            # Initialize the process end time for each machine
            heapq.heappush(self.events, Event(
                machine_name=machine['machine'],
                # Initial time for the machine
                time=machine['processing_time'],
                status=EventStatus.JOB_COMES,
            ))

        # while heap is not empty
        while self.events:
            # Get the job with the highest priority (lowest priority number)
            current_event: Event = heapq.heappop(self.events)
            if (isDebug):
                print(f"Current time: {current_event.time}")
                print(f"Processing event: {current_event}")

            if current_event.time >= self.total_processing_time:
                # If the current event time exceeds the total processing time, stop processing

                # TODO: deal with the remaining jobs in the queue
                break

            if (current_event.status == EventStatus.JOB_COMES):
                # push to job queue

                machine_property = next(
                    (m for m in self.machines if m['machine'] == current_event.machine_name), None)
                if machine_property is None:
                    if (isDebug):
                        print(
                            f"Machine {current_event.machine_name} not found in area {self.area_name}")
                    continue

                if (isDebug):
                    print(
                        f"Added a job to the queue for machine {machine_property["machine"]} at time {current_event.time}")

                process_end[current_event.machine_name] = current_event.time

                self.job_queue.append(Job(
                    produced_time=current_event.time,
                    # Placeholder for job duration
                    duration=machine_property["load_unload_time"],
                    machine_name=current_event.machine_name
                ))


            elif (current_event.status == EventStatus.WORKER_ENDS):
                # count the waiting time
                machine_property = next(
                    (m for m in self.machines if m['machine'] == current_event.machine_name), None)
                if machine_property is None:
                    if (isDebug):
                        print(
                            f"Machine {current_event.machine_name} not found in area {self.area_name}")
                    continue

                total_waiting_time += current_event.time - \
                    process_end[current_event.machine_name] - \
                    machine_property["load_unload_time"]

                if (isDebug):
                    print(
                        f"Worker finished job for machine {current_event.machine_name} at time {current_event.time}, waiting time: {total_waiting_time}")

                # write to file
                self.file.write(
                    f"{current_event.machine_name},{process_end[current_event.machine_name]},{current_event.time},{current_event.time - machine_property['load_unload_time']},{current_event.time}\n"
                )

                heapq.heappush(self.events, Event(
                    machine_name=machine_property['machine'],
                    # Initial time for the machine
                    time=machine_property['processing_time'] +
                    current_event.time,
                    status=EventStatus.JOB_COMES,
                ))

            # check if there are jobs in the queue
            if not self.job_queue:
                if (isDebug):
                    print("No jobs in the queue, waiting for new jobs.")
                continue

            # find out the available worker

            for worker in available_workers:

                if (self.job_queue):
                    # if job queue is not empty

                    # print("There is a job")

                    if worker.available(current_event.time):
                        if (isDebug):
                            print(
                                f"Worker {worker} is available at time {current_event.time}")
                            print("")
                        # Get the next job from the queue
                        # this worker is available
                        job = self.job_queue.pop(0)

                        machine_property = next(
                            (m for m in self.machines if m['machine'] == job.machine_name), None)
                        if machine_property is None:
                            if (isDebug):
                                print(
                                    f"Machine {job.machine_name} not found in area {self.area_name}")
                            continue

                        worker.picked(current_event.time,
                                      machine_property['load_unload_time'])

                        if (isDebug):
                            print(
                                f"Worker {worker} picked job {job} at time {current_event.time} for machine {job.machine_name} will finish at {worker.working_end}")
                            print("")

                        heapq.heappush(self.events, Event(
                            machine_name=job.machine_name,
                            time=machine_property['load_unload_time'] +
                            current_event.time,
                            status=EventStatus.WORKER_ENDS,
                        ))

        if (isDebug):
            print(
                f"Total waiting time for area {self.area_name}: {total_waiting_time}")

        return total_waiting_time
