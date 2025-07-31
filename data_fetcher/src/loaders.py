import json
import logging
import time

import requests
from pydantic import BaseModel

from common.db_connector import PostgresConnector
from common.event_source import EventSource


class BikeLocation(BaseModel):
    lat: float
    lon: float
    id: str


class BikeData(BaseModel):
    id: str
    bikes: int
    docks: int
    empty_docks: int
    standard_bikes: int
    ebikes: int
    temporary: bool


class DataExtractor:
    def __init__(self):
        self.url = "https://api.tfl.gov.uk/BikePoint/"
        self.es = EventSource()
        self.rate_limit = 50
        self.rate_limit_timeout = 35

    def get_bike_points(self):
        output = requests.get(self.url, timeout=200)
        points = [
            BikeLocation(lat=point["lat"], lon=point["lon"], id=point["id"])
            for point in output.json()
        ]
        return points

    def get_bike_data(self, bike_id: str):
        output = requests.get(f"{self.url}/{bike_id}", timeout=200)

        bikes = 0
        docks = 0
        ebikes = 0
        standard_bikes = 0
        empty_docks = 0
        temporary = False

        if output.status_code == 429:
            print("Sleeping...")
            while True:
                if output.status_code != 429:
                    break
                time.sleep(10)
                output = requests.get(f"{self.url}/{bike_id}", timeout=200)
        try:
            filtered_records = [
                record
                for record in output.json()["additionalProperties"]
                if record["key"] in ["NbBikes", "NbDocks"]
            ]
            for record in filtered_records:
                if record["key"] == "NbBikes":
                    bikes = record["value"]
                elif record["key"] == "NbDocks":
                    docks = record["value"]
                elif record["key"] == "NbEBikes":
                    ebikes = record["value"]
                elif record["key"] == "NbStandardBikes":
                    standard_bikes = record["value"]
                elif record["key"] == "NbEmptyDocks":
                    empty_docks = record["value"]
                elif record["key"] == "Temporary":
                    if record["value"] == "false":
                        temporary = False
                    else:
                        temporary = True

            return BikeData(
                id=bike_id,
                docks=docks,
                bikes=bikes,
                empty_docks=empty_docks,
                ebikes=ebikes,
                standard_bikes=standard_bikes,
                temporary=temporary,
            )
        except Exception as e:
            print(output.text)
            raise e

    def refresh(self):
        points = self.get_bike_points()
        for point in points:
            print(f"Point {point}")
            self.es.log_new_event("id", point)
            bike_data = self.get_bike_data(point.id)
            self.es.log_new_event("id", bike_data)


