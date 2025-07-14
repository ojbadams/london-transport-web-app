import json
import logging
import requests

from common.db_connector import PostgresConnector

class DataExtractor:
    def __init__(self):
        self.url = "https://api.tfl.gov.uk/BikePoint/"
        self.connector = PostgresConnector(host="localhost", user="postgres", password="postgres", dbname="tfl_data")
        self.check_timeout()
        self.init_database()

    def check_timeout(self):
        connect_try = 0
        while connect_try < 5:
            try:
                self.connector.connect()
                return True
            except:
                print("Failed to Connect")
                connect_try += 1
        raise Exception

    def init_database(self):
        self.connector.execute_query("CREATE SCHEMA IF NOT EXISTS staging;")
        self.connector.execute_query("""
                    CREATE TABLE IF NOT EXISTS staging.raw_api_data (
                        id serial,
                        created_at TIMESTAMP DEFAULT NOW(),
                        data JSON,
                        processed Bool DEFAULT False);
                        """)

    def fetch_data(self):
        output = requests.get(self.url, timeout=200)
        logging.info("Starting process")

        if output.status_code == 200:
            self.connector.execute_query(f"INSERT INTO staging.raw_api_data (data) VALUES (%s)", (json.dumps(output.json()), ))