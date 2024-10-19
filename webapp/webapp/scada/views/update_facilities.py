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

import json


# =======================================================================================================================
class UpdateFacilitiesView(View):
    @staticmethod
    def get(request, user_id):
        template = "scada/update_facilities.html"
        context = {
            "user_id": user_id,
        }
        return render(request, template, context)

    @staticmethod
    def post(request, user_id):
        pass


class AddFacilitiesView(View):
    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        try:
            # Parse JSON body
            body = json.loads(request.body.decode("utf-8"))
            user_id = body.get("user_id")
            facility_id = body.get("facility_id")

            if not user_id or not facility_id:
                return JsonResponse(
                    {"error": "Invalid input, either missing user_id or facility_id"},
                    status=400,
                )

            # Add facility to the user
            dbsession = next(get_dbsession())  # Get the SQLAlchemy session
            new_facility = Facility(user_id=user_id, facility_id=facility_id)

            try:
                dbsession.add(new_facility)
                dbsession.commit()
                return JsonResponse({"success": True})
            except Exception as e:
                dbsession.rollback()
                return JsonResponse({"success": False, "error": str(e)})
            finally:
                dbsession.close()

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)


class RemoveFacilitiesView(View):
    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        try:
            # Parse JSON body
            body = json.loads(request.body.decode("utf-8"))
            user_id = body.get("user_id")
            facility_id = body.get("facility_id")

            if not user_id or not facility_id:
                return JsonResponse(
                    {"error": "Invalid input, either missing user_id or facility_id"},
                    status=400,
                )

            # Remove facility from the user
            dbsession = next(get_dbsession())  # Get the SQLAlchemy session
            facility = (
                dbsession.query(Facility)
                .filter_by(user_id=user_id, facility_id=facility_id)
                .first()
            )

            if facility:
                try:
                    dbsession.delete(facility)
                    dbsession.commit()
                    return JsonResponse({"success": True})
                except Exception as e:
                    dbsession.rollback()
                    return JsonResponse({"success": False, "error": str(e)})
                finally:
                    dbsession.close()
            else:
                return JsonResponse({"success": False, "error": "Facility not found."})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
