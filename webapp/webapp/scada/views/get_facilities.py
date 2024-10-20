from django.shortcuts import render, redirect, get_object_or_404

from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.views import generic
from django.views import View
from django.http import HttpResponse, JsonResponse

from ..sqlalchemy_setup import get_dbsession
from sqlalchemy.orm import sessionmaker
from ..models.auth_entity import AuthEntity
from ..models.facility import Facility
from ..forms.contact import ContactForm
from ..forms.subscribe import SubscribeForm
from ..forms.sign_up import SignUpForm
from ..forms.profile import ProfileForm

import environ

from ..oracle_connection import fetch_one_from_oracle, fetch_all_from_oracle


# =======================================================================================================================
class GetFacilitiesView(View):
    @staticmethod
    def get(request):
        user_id = request.GET.get("user_id", None)
        query = f"""
                    SELECT DISTINCT FACILITY_ID as facility_id
                    FROM PETRINEX_VOLUMETRIC_DATA
                    ORDER BY FACILITY_ID ASC
                """
        facilities = fetch_all_from_oracle(query)  # Fetching from Oracle DB
        facilities = [f[0] for f in facilities]

        # check user self
        dbsession = next(get_dbsession())  # Get the SQLAlchemy session
        user_facilities = dbsession.query(Facility).filter_by(user_id=user_id).all()
        dbsession.close()

        if not user_facilities:
            results = [{"id": f, "action": "Add"} for f in facilities]
        else:
            user_facilities = [f.facility_id for f in user_facilities]
            results = [
                {"id": f, "action": "Remove" if f in user_facilities else "Add"}
                for f in facilities
            ]

        return JsonResponse({"facilities": results})

    @staticmethod
    def post(request):
        pass


class ReloadFacilitiesView(View):
    @staticmethod
    def get(request):
        user_id = request.GET.get("user_id", None)

        dbsession = next(get_dbsession())
        user_facilities = (
            dbsession.query(Facility.facility_id).filter_by(user_id=user_id).all()
        )
        dbsession.close()

        # Convert the list of tuples (because .all() returns a list of tuples)
        user_facilities = [(facility[0], facility[0]) for facility in user_facilities]

        return JsonResponse({"facilities": user_facilities})

    @staticmethod
    def post(request):
        pass
