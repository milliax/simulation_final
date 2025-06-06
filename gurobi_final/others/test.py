from gurobipy import Model, GRB, quicksum
import math

# Machine definition
machines = [
    {"machine": "PR_1", "processing_time": 60, "load_unload_time": 3},
    {"machine": "PR_2", "processing_time": 60, "load_unload_time": 3},
    {"machine": "DA_1", "processing_time": 17, "load_unload_time": 3},
    {"machine": "DA_2", "processing_time": 17, "load_unload_time": 3},
    {"machine": "DA_3", "processing_time": 17, "load_unload_time": 3},
    {"machine": "DA_4", "processing_time": 17, "load_unload_time": 3},
    {"machine": "DA_5", "processing_time": 17, "load_unload_time": 3},
    {"machine": "DA_6", "processing_time": 17, "load_unload_time": 3},
    {"machine": "DA_7", "processing_time": 17, "load_unload_time": 3},
    {"machine": "DA_8", "processing_time": 17, "load_unload_time": 3},
    {"machine": "85_1", "processing_time": 80, "load_unload_time": 2},
    {"machine": "85_2", "processing_time": 80, "load_unload_time": 2},
    {"machine": "85_3", "processing_time": 80, "load_unload_time": 2},
    {"machine": "DP_1", "processing_time": 50, "load_unload_time": 2},
    {"machine": "DP_2", "processing_time": 50, "load_unload_time": 2},
    {"machine": "DP_3", "processing_time": 50, "load_unload_time": 2},
    {"machine": "DP_4", "processing_time": 50, "load_unload_time": 2},
]

T_max = 1000
M = 1e6

# Compute max cycles for each machine
for m in machines:
    cycle_time = m["processing_time"] + m["load_unload_time"]
    m["max_cycles"] = math.floor(T_max / cycle_time)

# Initialize model
model = Model("MachineCycleScheduling")
model.setParam("OutputFlag", 1)

# Variables
start, finish, load_start, wait, load_end = {}, {}, {}, {}, {}
active = {}  # binary flag for whether cycle is used
load_jobs = []  # all load tasks for disjunctive constraints

for m in machines:
    name = m["machine"]
    p = m["processing_time"]
    l = m["load_unload_time"]
    max_c = m["max_cycles"]

    for c in range(max_c):
        key = (name, c)
        active[key] = model.addVar(vtype=GRB.BINARY, name=f"active_{name}_{c}")
        start[key] = model.addVar(lb=0, ub=T_max, name=f"start_{name}_{c}")
        finish[key] = model.addVar(lb=0, ub=T_max, name=f"finish_{name}_{c}")
        load_start[key] = model.addVar(lb=0, ub=T_max, name=f"load_start_{name}_{c}")
        wait[key] = model.addVar(lb=0, ub=T_max, name=f"wait_{name}_{c}")
        load_end[key] = model.addVar(lb=0, ub=T_max, name=f"load_end_{name}_{c}")

        # Constraints for processing and loading
        model.addConstr(finish[key] == start[key] + p * active[key], name=f"finish_def_{name}_{c}")
        model.addConstr(load_start[key] >= finish[key], name=f"load_after_process_{name}_{c}")
        model.addConstr(wait[key] == load_start[key] - finish[key], name=f"wait_def_{name}_{c}")
        model.addConstr(load_end[key] == load_start[key] + l * active[key], name=f"load_end_def_{name}_{c}")
        model.addConstr(load_end[key] <= T_max + (1 - active[key]) * M, name=f"within_Tmax_{name}_{c}")

        load_jobs.append((key, load_start[key], l, active[key]))

        # If not first cycle, must follow previous load
        if c > 0:
            prev_key = (name, c - 1)
            model.addConstr(start[key] >= load_end[prev_key], name=f"cycle_order_{name}_{c}")

# Worker disjunctive constraint: no two loading tasks can overlap
for i in range(len(load_jobs)):
    key_i, s_i, dur_i, act_i = load_jobs[i]
    for j in range(i + 1, len(load_jobs)):
        key_j, s_j, dur_j, act_j = load_jobs[j]
        y = model.addVar(vtype=GRB.BINARY, name=f"y_{key_i}_{key_j}")

        # load_i before load_j
        model.addConstr(s_i + dur_i * act_i <= s_j + M * (1 - y), name=f"disj1_{key_i}_{key_j}")
        # load_j before load_i
        model.addConstr(s_j + dur_j * act_j <= s_i + M * y, name=f"disj2_{key_i}_{key_j}")

# Objective: minimize total wait time
model.setObjective(quicksum(wait[k] for k in wait), GRB.MINIMIZE)

model.optimize()

# Output results
for m in machines:
    name = m["machine"]
    print(f"\nMachine {name}")
    for c in range(m["max_cycles"]):
        key = (name, c)
        if active[key].X > 0.5:
            print(f"  Cycle {c}: Start {start[key].X:.1f}, Finish {finish[key].X:.1f}, "
                  f"Load {load_start[key].X:.1f} → {load_end[key].X:.1f}, Wait {wait[key].X:.1f}")
