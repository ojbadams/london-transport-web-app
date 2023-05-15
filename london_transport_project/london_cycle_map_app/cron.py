import json
import logging
import requests

from london_cycle_map_app.models import BikePointCapacity

def update_cycles_avaliable():
    """ Update BikePoints """
    output = requests.get("https://api.tfl.gov.uk/BikePoint/", timeout=200)
    logging.info("Starting process")
    print("here")
    # data_keys_to_extract = ["NbBikes", "NbDocks"]

    if output.status_code == 200:
        json_output = json.loads(output.text)

        for bike_list in json_output:
            id = bike_list["id"]
            id = id.replace("BikePoints_", "")

            bikes = [i["value"] for i in bike_list["additionalProperties"] if i["key"] == "NbBikes"][0]
            docks = [i["value"] for i in bike_list["additionalProperties"] if i["key"] == "NbDocks"][0]

            BikePointCapacity.objects.update_or_create(
                id=int(id), defaults={"capacity":int(docks), "in_use":int(bikes)})
