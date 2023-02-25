from django.urls import path

from dal import autocomplete
from django.urls import re_path as url

from london_cycle_map_app.models  import BikePointLocation

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.get_directions, name='index'),
    url(
        'bp/$',
        autocomplete.Select2QuerySetView.as_view(model=BikePointLocation),
        name='select2_fk',
    ),
]