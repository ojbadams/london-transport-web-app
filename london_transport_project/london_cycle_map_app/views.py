from django.shortcuts import render, redirect

from london_cycle_map_app.models import BikePointLocation, BikePointCapacity
from london_cycle_map_app.forms import SearchForm

from dal import autocomplete

import json

# Create your views here.

class BikePointAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return BikePointLocation.objects.none()

        qs = BikePointLocation.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

def index(request):
    """ Main Page """
    final_bike = []

    for i in BikePointLocation.objects.all():
        try:
            capacity_data = BikePointCapacity.objects.get(id=i.id)
            final_bike.append([i.lat, i.lon, i.common_name, capacity_data.in_use, capacity_data.capacity])
        except BikePointCapacity.DoesNotExist:
            final_bike.append([i.lat, i.lon, i.common_name, "??", "??"])

    map_centre_name = request.session.get("map_center_name")

    args = {}
    args["centre_lat_lon"] = [51.505, -0.09]
    args["default_zoom"] = 12

    if map_centre_name is not None:
        try:
            obj = BikePointLocation.objects.get(common_name=map_centre_name)
            args["centre_lat_lon"] = [obj.lat, obj.lon]
            args["default_zoom"] = 20

        except BikePointLocation.DoesNotExist:
            pass

    args["lat_lon"] = json.dumps(final_bike)
    args["form"] = SearchForm()

    return render(request, 'london_cycle_map_app/index.html', args)


def get_directions(request):
    """
    When the search button is pressed, take the data in the search box, search for lat, lon
    and orient the map
    """
    if request.method == "POST":
        form = SearchForm(request.POST)
        print(form.is_valid())
        print(request.POST)
        print(form.errors)
        print(form.non_field_errors)

        if form.is_valid():
            searched_point = form.cleaned_data.get("start_location")
            print(searched_point)
            request.session["map_center_name"] = searched_point
            return redirect(index)
    else:
        form = SearchForm()

    return redirect(index)
