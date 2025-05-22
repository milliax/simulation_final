import gurobipy as gp

from gurobipy import GRB
import pandas as pd


class AreaDispatcher:
    def __init__(self, number_of_workers, machine, iteration):
        self.number_of_workers = number_of_workers
        self.machines = machine
        self.iteration = iteration

    def dispatch(self, area_name):
        # Dispatch logic for the area

        n_machines = len(self.machines)
        n_workers = self.number_of_workers

        processing_time = []   # 加工時間  (HM_2, DU_1, DU_2, MX_1, MX_2 之類)
        loading_time = []   # 裝卸貨時間
        machine_name = []

        for mach in self.machines:
            processing_time.append(mach.processing_time)
            loading_time.append(mach.load_unload_time)
            machine_name.append(mach.machine)


        M = sum(p) + sum(l)

        return total_waiting_time
