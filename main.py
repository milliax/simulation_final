
from database import Database
from area import AreaDispatcher
import pandas as pd

import os
from typing import Any
from type import DispatchingRule

from dotenv import load_dotenv
load_dotenv()


isDev = os.getenv("DEBUG") == "true"

if __name__ == "__main__":
    print("Program started")

    resources = Database(user="11302_SIM",
                         password="11302",
                         hostname="140.113.59.168")

    resources.connect()

    query = resources.execute_query(
        "SELECT * FROM SIM_STUDENT. SIM_ALLOCATE_DISPATCH_1")

    query2 = resources.execute_query(
        "SELECT * FROM SIM_STUDENT. SIM_ALLOCATE_DISPATCH_2")

    resources.close()

    iter: list[dict[str, int]] = []

    if not query or not query2:
        print("Database query returned no results.")
        exit(1)

    # print(query2)

    for q in query2:
        i = {
            "id": q[0],
            "workers": q[1],
            "limitation": q[2],
        }
        iter.append(i)

    """ Tests from database """
    print("tests: ")
    for i in iter:
        print("id: ", i["id"])
        print("workers: ", i["workers"])
        print("time limitations: ", i["limitation"])

    layout = {}

    for row in query:
        # print(row)
        instance = row[0]
        area = row[1]
        machine = row[2]
        processing_time = row[3]
        load_unload_time = row[4]

        if instance not in layout:
            layout[instance] = {}

        if area not in layout[instance]:
            layout[instance][area] = []

        layout[instance][area].append({
            "machine": machine,
            "processing_time": processing_time * 60,
            "load_unload_time": load_unload_time * 60
        })

    # print(dictionary)

    caching: dict[str, dict[DispatchingRule, dict[int, int]]] = {}

    """
    caching: {
        "area_name": {
            "dispatching_method":{
                "worker_cnt": processing_time
            }
        }
    }
    
    """

    result_to_write: list[dict[str, int | str | float]] = []

    for e in iter:
        print(f"Instance: {e['id']}")
        print(f"  Total Workers: {e['workers']}")
        print(f"  Time limitation: {e['limitation']} seconds")

        better_solution_found = True
        minimum_waiting_time = 1e10

        # distribut e['workers'] workers to areas

        # using instance 1 for all tasks
        number_of_areas = len(layout['1'].keys())

        # 0606: update permutations typo into permutation
        permutation: list[int] = []
        method: list[DispatchingRule] = []

        # getting started with the minimum number of workers as each area for one

        worker_available = e["workers"]

        for i in range(number_of_areas):
            if e["workers"] > 0:
                permutation.append(1)
                worker_available -= 1
            else:
                permutation.append(0)
                print("  Error: No more workers available, setting to 0")

            method.append(DispatchingRule.FIFO)

        areas = len(layout['1'].keys())
        machines_in_each_area: dict[str, list[dict[str, str | int]]] = {
            area: layout['1'][area] for area in layout['1'].keys()}

        total_machine_number = 0

        for area in machines_in_each_area:
            total_machine_number += len(machines_in_each_area[area])

        print(f"  Worker_available: {worker_available}")
        print(f"  Total machines in all areas: {total_machine_number}")
        print(f"  Initial permutation: {permutation}")

        while worker_available > 0 and sum(permutation) <= total_machine_number:
            # as long as there are workers available, distribute them evenly
            # get the total number of machines in all areas

            # i could still add more workers to the areas

            area_to_add = None
            lowest_waiting_time = 1e10

            # finding the next area to add a worker to
            for area_idx in range(len(permutation)):
                new_permutation = permutation.copy()
                new_permutation[area_idx] += 1

                new_waiting_time = 0
                results = []

                # calculate the waiting time for each area
                for tied in zip(new_permutation, layout['1'].keys()):
                    # print(f"tied: {tied}")

                    if isDev:
                        print(f"  Area: {tied[1]}, Workers: {tied[0]}")

                    # run for each dispatching method FIFO, LIFO, SPTF, LPTF

                    best_result = int(1e10)
                    # should be None, but we need to set it to something
                    best_method = DispatchingRule.FIFO

                    for dispatching_method in [DispatchingRule.FIFO, DispatchingRule.LIFO, DispatchingRule.SPTF, DispatchingRule.LPTF]:
                        if caching.get(tied[1]) is not None and caching[tied[1]].get(dispatching_method) is not None and caching[tied[1]][dispatching_method].get(tied[0]) is not None:
                            result = caching[tied[1]
                                             ][dispatching_method][tied[0]]

                            print(f"  Area {tied[1]} with {tied[0]} workers, method: {dispatching_method}, time: {result}")

                            if (result < best_result):
                                best_result = result
                                best_method = dispatching_method

                            if isDev:
                                print(
                                    f"  HIT cache for area {tied[1]} with {tied[0]} workers")
                            continue

                        if isDev:
                            print(
                                f"  Dispatching method: {dispatching_method}")

                        a = AreaDispatcher(
                            number_of_workers=tied[0],
                            # using instance 1 for all tasks
                            machines=layout['1'][tied[1]],
                            total_processing_time=e["limitation"],
                            area_name=tied[1],

                            dispatching_rule=dispatching_method,  # using FIFO for now
                        )

                        result = a.dispatch()

                        if result < best_result:
                            best_result = result
                            best_method = dispatching_method

                        caching.setdefault(tied[1], {}).setdefault(
                            dispatching_method, {}
                        ).setdefault(tied[0], best_result)

                        print(f"  Area {tied[1]} with {tied[0]} workers, method: {dispatching_method}, time: {result}")

                    if isDev:
                        print(
                            f"  Processing time for area {tied[1]} with {tied[0]}, method: {best_method}, time: {best_result}")

                    results.append(best_result)
                    method[area_idx] = best_method
                    # caching.setdefault(tied[1], {})[tied[0]] = best_result

                if (new_waiting_time < lowest_waiting_time):
                    lowest_waiting_time = new_waiting_time
                    area_to_add = area_idx

            if area_to_add is not None:
                permutation[area_to_add] += 1
                worker_available -= 1
                minimum_waiting_time = lowest_waiting_time

                print(f"     updated permutation: {permutation}")
                print(f"     woker available: {worker_available}")

                if isDev:
                    print(
                        f"  Adding worker to area {layout['1'].keys()[area_to_add]}: {permutation}")

            # for machine in dictionary[key][area]:
            #     print(f"    Machine: {machine['machine']}")
            #     print(f"      Processing time: {machine['processing_time']}")
            #     print(f"      Load/unload time: {machine['load_unload_time']}")

        result_to_write.append({
            "INSTANCE": e["id"],
            # average idle time in minutes
            "AVERAGE_IDLE_TIME": int(minimum_waiting_time/60) / (len(layout["1"]["ETCH"]) + len(layout["1"]["PHOTO"]) + len(layout["1"]["TF"])),
            "STAFF_IN_AREA1": permutation[0],
            "STAFF_IN_AREA2": permutation[1],
            "STAFF_IN_AREA3": permutation[2],

            "DISPATCH_IN_AREA1": method[0].value,
            "DISPATCH_IN_AREA2": method[1].value,
            "DISPATCH_IN_AREA3": method[2].value,
        })

        print(
            f"Best permutation: {permutation} with method: {method[0]}, method: {method[1]},method: {method[2]}, time {minimum_waiting_time/60} minutes")

    # print(f"caching: {caching}")

    # skip to write to database
    exit(0)

    """ write result back to database """
    db = Database(user="TEAM_11",
                  password="team11",
                  hostname="140.113.59.168")

    db.connect()

    print("Writing results to database...")
    print(result_to_write)

    for result in result_to_write:
        result = db.execute_query("""MERGE INTO RESULT_TEMPLATE dst
USING (
    SELECT
        :instance AS INSTANCE,
        :average_idle_time AS AVERAGE_IDLE_TIME,
        :staff_area1 AS STAFF_IN_AREA1,
        :staff_area2 AS STAFF_IN_AREA2,
        :staff_area3 AS STAFF_IN_AREA3,
        :dispatch_area1 AS DISPATCH_IN_AREA1,
        :dispatch_area2 AS DISPATCH_IN_AREA2,
        :dispatch_area3 AS DISPATCH_IN_AREA3
    FROM dual
) src
ON (dst.INSTANCE = src.INSTANCE)
WHEN MATCHED THEN
    UPDATE SET
        dst.AVERAGE_IDLE_TIME = src.AVERAGE_IDLE_TIME,
        dst.STAFF_IN_AREA1 = src.STAFF_IN_AREA1,
        dst.STAFF_IN_AREA2 = src.STAFF_IN_AREA2,
        dst.STAFF_IN_AREA3 = src.STAFF_IN_AREA3,
        dst.DISPATCH_IN_AREA1 = src.DISPATCH_IN_AREA1,
        dst.DISPATCH_IN_AREA2 = src.DISPATCH_IN_AREA2,
        dst.DISPATCH_IN_AREA3 = src.DISPATCH_IN_AREA3
WHEN NOT MATCHED THEN
    INSERT (
        INSTANCE,
        AVERAGE_IDLE_TIME,
        STAFF_IN_AREA1,
        STAFF_IN_AREA2,
        STAFF_IN_AREA3,
        DISPATCH_IN_AREA1,
        DISPATCH_IN_AREA2,
        DISPATCH_IN_AREA3
    )
    VALUES (
        src.INSTANCE,
        src.AVERAGE_IDLE_TIME,
        src.STAFF_IN_AREA1,
        src.STAFF_IN_AREA2,
        src.STAFF_IN_AREA3,
        src.DISPATCH_IN_AREA1,
        src.DISPATCH_IN_AREA2,
        src.DISPATCH_IN_AREA3
    )""", {"instance": result["INSTANCE"],
            "average_idle_time": (result["AVERAGE_IDLE_TIME"]),
            "staff_area1": result["STAFF_IN_AREA1"],
            "staff_area2": result["STAFF_IN_AREA2"],
            "staff_area3": result["STAFF_IN_AREA3"],
            "dispatch_area1": result["DISPATCH_IN_AREA1"],
            "dispatch_area2": result["DISPATCH_IN_AREA2"],
            "dispatch_area3": result['DISPATCH_IN_AREA3']})

    # plot the best permutation with gannt chart

    db.close()
    print("Results written to database successfully.")
