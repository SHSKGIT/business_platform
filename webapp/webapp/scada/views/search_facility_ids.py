from django.shortcuts import render, redirect, get_object_or_404

from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.views import generic
from django.views import View
from django.http import HttpResponse, JsonResponse

from ..sqlalchemy_setup import get_dbsession
from sqlalchemy.orm import sessionmaker
from ..models.auth_entity import AuthEntity
from ..forms.contact import ContactForm
from ..forms.subscribe import SubscribeForm
from ..forms.sign_in import SignInForm
from ..forms.ai import AiForm
from ..forms.pbr import PBRForm

from ..oracle_connection import fetch_one_from_oracle, fetch_all_from_oracle


# =======================================================================================================================
class SearchFacilityIdsView(View):
    @staticmethod
    def get(request):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            term = request.GET.get("term", "")  # Get the search term from AJAX
            query = f"""
                        SELECT DISTINCT FACILITY_ID as facility_id,
                                COUNT(FACILITY_ID)
                        FROM PETRINEX_VOLUMETRIC_DATA
                        WHERE lower(FACILITY_ID) LIKE lower('%{term}%')
                        GROUP BY FACILITY_ID
                        ORDER BY FACILITY_ID
                    """
            facilities = fetch_all_from_oracle(query)
            results = [{"id": f[0], "label": f[0]} for f in facilities]
            return JsonResponse(results, safe=False)

        # If not an AJAX request, return an empty response or handle it otherwise
        return JsonResponse({"error": "Invalid request"}, status=400)
