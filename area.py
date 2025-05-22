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

        iterations_with_workers = [index for index in range(self.iteration)]

        processing_time = []   # 加工時間  (HM_2, DU_1, DU_2, MX_1, MX_2 之類)
        loading_time = []   # 裝卸貨時間
        machine_name = []

        for i in range(self.machines):
            processing_time.append(self.machine[i].processing_time)
            loading_time.append(self.machine[i].load_unload_time)
            machine_name.append("{mach.machine}-{i}")

        # Create a Gurobi model
        m = gp.Model('load_unload_scheduling')

        # s = m.addVars(n_machines, lb=0.0, name='start')          # 裝卸貨開始
        # w = m.addVars(n_machines, lb=0.0, name='wait')           # 等待時間

        # set variables
        processing_start = m.addVars(machine_name,
                                     iterations_with_workers,

                                     self.iteration,
                                     vtype=GRB.BINARY,
                                     name='processing_time')  # 加工時間

        loading_start = m.addVars(machine_name,
                                  iterations_with_workers,

                                  self.iteration,
                                  vtype=GRB.BINARY,
                                  name='loading_time')

        # set constraints

        for i in range(self.machines):
            for k in range(self.iteration):

                if (i == len(self.machines)-1):
                    break

                m.addConstr(
                    processing_start[i, k] + processing_time[i] <= processing_start[i, k+1])
                
                m.addConstr(
                    loading_start[i, k] + loading_time[i] <= loading_start[i, k+1])

                m.addConstr(
                    loading_start[i, k] + processing_time[i] <= loading_start[i, k+1])

        # M = sum(p) + sum(l)

        # number of operations
        ops = [(i, k)
               for i in self.machines for k in range(1, self.iteration+1)]

        # set objective function
        m.setObjective(gp.quicksum(processing_start[i, k] - loading_start[i, k]
                                   for i, k in ops), GRB.MINIMIZE)

        # Optimize the model
        m.optimize()

        # Check if the model has an optimal solution
        if m.status == GRB.OPTIMAL:
            print('Optimal solution found')
            # Extract the optimal values of the variables
            processing_start_values = m.getAttr('x', processing_start)
            loading_start_values = m.getAttr('x', loading_start)

            # Create a DataFrame to store the results
            results = pd.DataFrame(
                columns=['Machine', 'Processing Start', 'Loading Start'])

            for i in range(self.machines):
                for k in range(self.iteration):
                    results = results.append({
                        'Machine': f'Machine {i}',
                        'Processing Start': processing_start_values[i, k],
                        'Loading Start': loading_start_values[i, k]
                    }, ignore_index=True)

            print(results)
        else:
            print('No optimal solution found')

        return total_waiting_time
