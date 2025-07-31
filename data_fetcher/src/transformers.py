from common.db_connector import PostgresConnector


class DataTransformer:
    def __init__(self):
        self.connector = PostgresConnector(
            host="localhost", user="postgres", password="postgres", dbname="tfl_data"
        )
        self._init_database()

    def _init_database(self):
        self.connector.execute_query("CREATE SCHEMA IF NOT EXISTS core;")
        self.connector.execute_query(
            """
                    CREATE TABLE IF NOT EXISTS core.docks (
                        id serial,
                        lat float,
                        lon float,
                        tfl_id text PRIMARY KEY)
                        """
        )

