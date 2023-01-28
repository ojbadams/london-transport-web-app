from django.shortcuts import render

from models import BikePointLocation

import logging
import json

# Create your views here.

def index(request):
    """ Main Page """
    one_record = BikePointLocation.objects.all()

    lat_lon = [[i.lat, i.lon, i.common_name] for i in one_record]
    logging.info(lat_lon)

    args = {}
    args["lat_lon"] = json.dumps(lat_lon)

    return render(request, 'london_cycle_map_app/index.html', args)
