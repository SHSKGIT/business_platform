from django import forms
from .custom_fields import CustomCharField
from ..oracle_connection import fetch_one_from_oracle, fetch_all_from_oracle

from ..sqlalchemy_setup import get_dbsession
from ..models.facility import Facility


class PBRForm(forms.Form):
    UNIT_CHOICES = [
        ("metric", "Metric"),
        ("imperial", "Imperial"),
    ]

    pbr_battery_code = forms.ChoiceField(
        label="* Facility ID",
        required=True,
        widget=forms.Select(
            attrs={
                "id": "pbr_battery_code",
                "class": "span12",
                "placeholder": "* Facility ID",
                # "type": "text",
            }
        ),
        error_messages={
            "required": "Please select a facility ID.",
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

    def __init__(self, *args, user_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user_id:
            dbsession = next(get_dbsession())  # Get the SQLAlchemy session
            battery_code_choices = (
                dbsession.query(Facility.facility_id).filter_by(user_id=user_id).all()
            )
            dbsession.close()

            # Convert the list of tuples (because .all() returns a list of tuples)
            battery_code_choices = [
                (facility[0], facility[0]) for facility in battery_code_choices
            ]

            battery_code_choices.insert(0, ("", "Select a facility ID"))
            self.fields["pbr_battery_code"].choices = battery_code_choices
