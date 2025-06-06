# connection using oracle cx_Oracle

import cx_Oracle


class Database:
    def __init__(self, user, password, hostname):
        self.user = user
        self.password = password
        self.hostname = hostname
        self.connection = None

    def connect(self):
        try:
            # dsn_tns = cx_Oracle.makedsn(
            #     self.hostname, '1521', sid="xe")
            # self.connection = cx_Oracle.connect(
            # user=self.user, password=self.password, dsn=dsn_tns)

            self.connection = cx_Oracle.connect("{}/{}@{}"
                                                .format(self.user, self.password, self.hostname))

            print("Connection successful")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            print(f"Error code: {error.code}")
            print(f"Error message: {error.message}")

    def close(self):
        if self.connection:
            self.connection.close()
            print("Connection closed")

    def execute_query(self, query, params=None):
        if self.connection:
            cursor = self.connection.cursor()
            try:
                if params is None:
                    params = {}
                # print(query, params)
                cursor.execute(query, params)

                # Only fetch results if it's a SELECT
                if query.strip().lower().startswith("select"):
                    result = cursor.fetchall()
                    return result
                else:
                    self.connection.commit()  # commit for INSERT/UPDATE/MERGE
                    return None
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                print(f"Error code: {error.code}")
                print(f"Error message: {error.message}")
            finally:
                cursor.close()
        else:
            print("No connection to the database")