# Gurobi

from db_connector import Database
from area import AreaDispatcher

from struct import Argument
from area import AreaDispatcher

if __name__ == "__main__":

    print("Program started")

    # Initialize the database connection

    resources = Database(user="11302_SIM",
                         password="11302",
                         hostname="140.113.59.168")

    resources.connect()

    query = resources.execute_query(
        "SELECT * FROM SIM_STUDENT. SIM_ALLOCATE_DISPATCH_1")

    query2 = resources.execute_query(
        "SELECT * FROM SIM_STUDENT. SIM_ALLOCATE_DISPATCH_2")

    resources.close()

    # print(query2)

    iter = []

    for q in query2:
        i = {
            "id": q[0],
            "workers": q[1],
            "limitation": q[2],
        }
        iter.append(i)

    print("tests: ")
    for i in iter:
        print("id: ", i["id"])
        print("workers: ", i["workers"])
        print("time limitations: ", i["limitation"])

    print("")

    # print result

    # print result of resources

    # reformat the data into dictionary

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
            "processing_time": processing_time,
            "load_unload_time": load_unload_time
        })

    # print(dictionary)

    for key in layout.keys():
        print(f"Instance: {key}")

        for area in layout[key]:
            print(f"  Area: {area}")
            a = AreaDispatcher(
                number_of_workers=1,
                machines=layout[key][area],
                total_processing_time=1000,
                area_name=area,
            )
            result = a.dispatch()

            # for machine in dictionary[key][area]:
            #     print(f"    Machine: {machine['machine']}")
            #     print(f"      Processing time: {machine['processing_time']}")
            #     print(f"      Load/unload time: {machine['load_unload_time']}")

            print(f"Total waiting time: {result}")

    # db = Database(user="TEAM_11",
    #               password="team11",
    #               hostname="140.113.59.168")

    # db.connect()

    # query = db.execute_query("SELECT * FROM SIM_STUDENT. SIM_ALLOCATE_DISPATCH_1")
