# Gurobi

from db_connector import Database
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
    resources.close()

    # print result

    # print result of resources

    # reformat the data into dictionary

    dictionary = {}

    for row in query:
        # print(row)
        instance = row[0]
        area = row[1]
        machine = row[2]
        processing_time = row[3]
        load_unload_time = row[4]

        if instance not in dictionary:
            dictionary[instance] = {}

        if area not in dictionary[instance]:
            dictionary[instance][area] = []

        dictionary[instance][area].append({
            "machine": machine,
            "processing_time": processing_time,
            "load_unload_time": load_unload_time
        })

    # print(dictionary)

    for key in dictionary.keys():
        print(f"Instance: {key}")

        for area in dictionary[key]:
            print(f"  Area: {area}")
            a = AreaDispatcher(
                number_of_workers=1,
                machine=dictionary[key][area],
                iteration=10
            )
            result = a.dispatch(area_name=area)

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
