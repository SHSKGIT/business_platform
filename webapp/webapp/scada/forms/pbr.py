from django import forms
from .custom_fields import CustomCharField


class PBRForm(forms.Form):
    pbr_battery_code = CustomCharField(
        label="* Battery Code",
        max_length=200,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "pbr_battery_code",
                "class": "span12",
                "placeholder": "* Battery Code",
                "type": "text",
            }
        ),
        error_messages={
            "required": "Please enter battery code.",
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
