"""Manage a Microsoft SQL Server database connection."""

import pyodbc
from solace_ai_connector.common.log import log


class MSSQLDatabase:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

        if ":" in self.host:
            self.host, self.port = self.host.split(":")
        else:
            self.port = 1433

    def cursor(self, **kwargs):
        if self.connection is None:
            self.connect()
        try:
            return self.connection.cursor(**kwargs)
        except Exception:  # pylint: disable=broad-except
            self.connect()
            return self.connection.cursor(**kwargs)

    def connect(self):
        # Try different ODBC drivers in order of preference
        drivers = [
            "ODBC Driver 18 for SQL Server",
            "ODBC Driver 17 for SQL Server", 
            "ODBC Driver 13 for SQL Server",
            "SQL Server"
        ]
        
        connection_string = None
        for driver in drivers:
            try:
                connection_string = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={self.host},{self.port};"
                    f"DATABASE={self.database};"
                    f"UID={self.user};"
                    f"PWD={self.password};"
                    "TrustServerCertificate=yes;"
                )
                self.connection = pyodbc.connect(connection_string, autocommit=True)
                break
            except pyodbc.Error as e:
                log.debug(f"Failed to connect with driver {driver}: {e}")
                continue
        
        if self.connection is None:
            raise ValueError(f"Could not connect to MSSQL server with any available driver. Tried: {', '.join(drivers)}")

    def close(self):
        if self.connection:
            self.connection.close()

    def execute(self, query, params=None):
        sanity = 3
        while True:
            try:
                cursor = self.cursor()
                cursor.execute(query, params)
                break
            except Exception as e:
                log.error("Database error: %s", e)
                sanity -= 1
                if sanity == 0:
                    raise e

        return cursor


def get_db_for_action(action_obj, sql_params=None):
    if sql_params:
        sql_host = sql_params.get("sql_host")
        sql_user = sql_params.get("sql_user")
        sql_password = sql_params.get("sql_password")
        sql_database = sql_params.get("sql_database")
    else:
        sql_host = action_obj.get_config("sql_host")
        sql_user = action_obj.get_config("sql_user")
        sql_password = action_obj.get_config("sql_password")
        sql_database = action_obj.get_config("sql_database")
    sql_db = None

    if sql_host and sql_user and sql_password and sql_database:
        sql_db = MSSQLDatabase(
            host=sql_host,
            user=sql_user,
            password=sql_password,
            database=sql_database,
        )

    if sql_db is None:
        raise ValueError(
            f"SQL database expected but not configured on {action_obj.__class__.__name__}"
        )

    return sql_db 