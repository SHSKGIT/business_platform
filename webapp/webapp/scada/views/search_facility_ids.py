from django.shortcuts import render, redirect, get_object_or_404

from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.views import generic
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator

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
            page = int(request.GET.get("page", 1))
            size = int(request.GET.get("size", 20))
            offset = (page - 1) * size  # Calculate the offset for pagination

            # Query to get all matching facility IDs
            query = f"""
                        SELECT DISTINCT FACILITY_ID as facility_id
                        FROM PETRINEX_VOLUMETRIC_DATA
                        WHERE lower(FACILITY_ID) LIKE lower('%{term}%')
                        ORDER BY FACILITY_ID ASC
                        OFFSET {offset} ROWS
                        FETCH NEXT {size} ROWS ONLY 
                    """
            facilities = fetch_all_from_oracle(query)  # Fetching from Oracle DB

            # Fetch total number of matching facilities for pagination purposes
            count_query = f"""
                             SELECT COUNT(DISTINCT FACILITY_ID) as facility_id
                             FROM PETRINEX_VOLUMETRIC_DATA
                             WHERE lower(FACILITY_ID) LIKE lower('%{term}%')
                            """
            total_count = int(fetch_one_from_oracle(count_query)[0])

            # Prepare results with facility id and pagination data
            results = [{"id": f[0], "label": f[0]} for f in facilities]

            return JsonResponse(
                {
                    "results": results,
                    "pagination": {
                        "more": (offset + size)
                        < total_count  # Check if more pages exist
                    },
                },
                safe=False,
            )

        # If not an AJAX request, return an empty response or handle it otherwise
        return JsonResponse({"error": "Invalid request"}, status=400)
