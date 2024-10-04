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
from ..forms.reset_password import ResetPasswordForm


# =======================================================================================================================
class ResetPasswordView(View):
    @staticmethod
    def get(request):
        template = "scada/reset_password.html"
        reset_password_form = ResetPasswordForm()
        context = {
            "reset_password_form": reset_password_form,
        }
        return render(request, template, context)

    @staticmethod
    def post(request):
        reset_password_form = ResetPasswordForm(request.POST)
        if reset_password_form.is_valid():
            username = reset_password_form.cleaned_data["username"]
            password = reset_password_form.cleaned_data["password"]
            # email = reset_password_form.cleaned_data["email"].lower()

            # check user
            dbsession = next(get_dbsession())  # Get the SQLAlchemy session
            user = (
                dbsession.query(AuthEntity).filter_by(username=username).one_or_none()
            )

            if user:
                # user exists, so update password
                user.set_password(password)

                dbsession.add(user)
                dbsession.commit()
                dbsession.refresh(user)
                dbsession.close()

                return JsonResponse(
                    {
                        "success": True,
                    }
                )
            else:
                # user doesn't exist, return no user found
                dbsession.close()

                return JsonResponse(
                    {
                        "success": False,
                        "reset_password_form_invalid_error": "Username doesn't exist.",
                    }
                )
        else:
            # If the form is not valid, render the form with errors
            template = "scada/reset_password.html"
            reset_password_form = ResetPasswordForm(request.POST)
            context = {
                "reset_password_form": reset_password_form,
            }
            return render(request, template, context)
