from common.db_connector import PostgresConnector


class DataTransformer:
    def __init__(self):
        self.connector = PostgresConnector(
            host="localhost", user="postgres", password="postgres", dbname="tfl_data"
        )
        self._init_data_base()

    def _init_data_base(self):
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

    def transform_bike_dock(self):
        records = self.connector.execute_query(
            "SELECT id, data FROM staging.raw_api_data WHERE processed = False"
        )
        ids_to_process = []
        for record in records:
            ids_to_process.append(record[0])
            for result in record[1]:
                lat, lon, tfl_id = result["lat"], result["lon"], result["id"]
                self.connector.execute_query(
                    "INSERT INTO core.docks (lat, lon, tfl_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
                    (
                        lat,
                        lon,
                        tfl_id,
                    ),
                )
