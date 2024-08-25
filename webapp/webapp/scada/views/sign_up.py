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
from ..forms.sign_up import SignUpForm


# =======================================================================================================================
class SignUpView(View):
    @staticmethod
    def get(request):
        template = "scada/sign_up.html"
        sign_up_form = SignUpForm()
        context = {
            "sign_up_form": sign_up_form,
        }
        return render(request, template, context)

    @staticmethod
    def post(request):
        pass
        sign_up_form = SignUpForm(request.POST)
        if sign_up_form.is_valid():
            username = sign_up_form.cleaned_data["username"].lower()
            password = sign_up_form.cleaned_data["password"]
            email = sign_up_form.cleaned_data["email"].lower()

            # check user
            dbsession = next(get_dbsession())  # Get the SQLAlchemy session
            user = (
                dbsession.query(AuthEntity).filter_by(username=username).one_or_none()
            )

            if user:
                dbsession.close()

                # user exists already
                return JsonResponse(
                    {
                        "success": False,
                        "sign_up_form_invalid_error": "Username exists, try others.",
                    }
                )
            else:
                # create a new user
                new_user = AuthEntity(username=username, email=email)
                new_user.set_password(password)
                dbsession.add(new_user)
                dbsession.commit()
                dbsession.refresh(new_user)
                dbsession.close()

                return JsonResponse(
                    {
                        "success": True,
                    }
                )
        else:
            # If the form is not valid, render the form with errors
            template = "scada/sign_up.html"
            sign_up_form = SignUpForm(request.POST)
            context = {
                "sign_up_form": sign_up_form,
            }
            return render(request, template, context)
