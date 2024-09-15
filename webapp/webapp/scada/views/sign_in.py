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


# =======================================================================================================================
class SignInView(View):
    @staticmethod
    def get(request):
        template = "scada/main.html"
        user_id = request.GET.get("user_id")
        ai_form = AiForm()
        context = {
            "user_id": user_id,
            "ai_form": ai_form,
        }
        return render(request, template, context)

    @staticmethod
    def post(request):
        sign_in_form = SignInForm(request.POST)
        if sign_in_form.is_valid():
            username = sign_in_form.cleaned_data["username"].lower()
            password = sign_in_form.cleaned_data["password"]

            # Query the database for the user
            dbsession = next(get_dbsession())  # Get the SQLAlchemy session
            user = (
                dbsession.query(AuthEntity).filter_by(username=username).one_or_none()
            )
            dbsession.close()

            if user and user.check_password(password):
                # Password matches, proceed with sign-in
                return JsonResponse(
                    {
                        "success": True,
                        "user_id": user.id,  # user object is not JSON serializable
                    }
                )
            else:
                # Invalid credentials
                return JsonResponse(
                    {
                        "success": False,
                        "sign_in_form_invalid_error": "Invalid username or password",
                    }
                )
        else:
            # If the form is not valid, render the form with errors
            template = "scada/home.html"
            subscribe_form = SubscribeForm(request.POST)
            contact_form = ContactForm(request.POST)
            context = {
                "contact_form": contact_form,
                "subscribe_form": subscribe_form,
                "sign_in_form": sign_in_form,
            }
            return render(request, template, context)
