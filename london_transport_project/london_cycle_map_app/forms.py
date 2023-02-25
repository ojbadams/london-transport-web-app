from django import forms

from dal import autocomplete

from london_cycle_map_app.models import BikePointLocation

class SearchForm(forms.Form):
    start_location = forms.ModelChoiceField(queryset=BikePointLocation.objects.values_list("common_name", flat=True),
                                            )


    end_location = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={"class": "form-control",
                                                                 "placeholder" : "Destination",
                                                                 "onchange" : "update_dropdown(this.value)"}))