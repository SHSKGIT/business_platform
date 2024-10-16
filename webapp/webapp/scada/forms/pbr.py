from django import forms
from .custom_fields import CustomCharField
from ..oracle_connection import fetch_one_from_oracle, fetch_all_from_oracle


class PBRForm(forms.Form):
    UNIT_CHOICES = [
        ("metric", "Metric"),
        ("imperial", "Imperial"),
    ]

    pbr_battery_code = CustomCharField(
        label="* Facility ID",
        max_length=200,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "pbr_battery_code",
                "class": "span12",
                "placeholder": "* Facility ID",
                "type": "text",
            }
        ),
        error_messages={
            "required": "Please select a facility ID.",
            "max_length": "Please enter no more than 200 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
    # Date field for selecting the start date
    pbr_start_date = forms.DateField(
        label="* From",
        required=True,
        widget=forms.DateInput(
            attrs={
                "id": "pbr_start_date",
                "class": "flatpickr span12",
                "placeholder": "* Start Date (YYYY-MM-DD)",  # Add placeholder for date format
                "type": "date",  # HTML5 date input type
            }
        ),
        error_messages={
            "required": "Please select a valid start date.",
        },
    )
    # Date field for selecting the end date
    pbr_end_date = forms.DateField(
        label="* To",
        required=True,
        widget=forms.DateInput(
            attrs={
                "id": "pbr_end_date",
                "class": "flatpickr span12",
                "placeholder": "* End Date (YYYY-MM-DD)",  # Add placeholder for date format
                "type": "date",  # HTML5 date input type
            }
        ),
        error_messages={
            "required": "Please select a valid end date.",
        },
    )
    unit = forms.ChoiceField(
        label="* Unit",
        choices=UNIT_CHOICES,
        initial="metric",  # Set default value to Metric
        required=True,
        widget=forms.Select(
            attrs={
                "id": "unit",
                "class": "span12",
            }
        ),
        error_messages={
            "required": "Please select a unit.",
        },
    )

    # def __init__(self, *args, **kwargs):
    #     super(PBRForm, self).__init__(*args, **kwargs)
    #     # Fetch data from the BatteryCode model and populate the dropdown
    #     query = f"""
    #                 SELECT DISTINCT FACILITY_ID
    #                 FROM PETRINEX_VOLUMETRIC_DATA
    #                 ORDER BY FACILITY_ID
    #             """
    #
    #     battery_code_choices = fetch_all_from_oracle(query)
    #     battery_code_choices.insert(0, ("", "Select a facility ID"))
    #     self.fields["pbr_battery_code"].choices = battery_code_choices
