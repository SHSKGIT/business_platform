from django.shortcuts import render, redirect, get_object_or_404

from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.views import generic
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import logout

from ..sqlalchemy_setup import get_dbsession
from sqlalchemy.orm import sessionmaker
from ..models.auth_entity import AuthEntity
from ..forms.contact import ContactForm
from ..forms.subscribe import SubscribeForm
from ..forms.sign_in import SignInForm


# =======================================================================================================================
class SignOutView(View):
    @staticmethod
    def get(request):
        # Log out the user
        logout(request)

        template = "scada/log_out.html"

        # Add headers to prevent caching
        response = render(request, template)
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"

        return response
