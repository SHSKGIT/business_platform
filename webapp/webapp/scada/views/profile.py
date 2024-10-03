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
from ..forms.profile import ProfileForm

import environ

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

ADMIN_EMAIL = [
    env("ADMIN_EMAIL_1"),
]


# =======================================================================================================================
class ProfileView(View):
    @staticmethod
    def get(request, user_id):
        template = "scada/profile.html"
        profile_form = ProfileForm(
            user_id=user_id
        )  # in order to set default value of each input
        context = {
            "profile_form": profile_form,
            "user_id": user_id,
        }
        return render(request, template, context)

    @staticmethod
    def post(request, user_id):
        profile_form = ProfileForm(request.POST)
        if profile_form.is_valid():
            username = profile_form.cleaned_data["username"]
            # password = sign_up_form.cleaned_data["password"]
            first_name = profile_form.cleaned_data["first_name"]
            last_name = profile_form.cleaned_data["last_name"]
            company = profile_form.cleaned_data["company"]
            phone = profile_form.cleaned_data["phone"]
            email = profile_form.cleaned_data["email"].lower()

            # check uniqueness of username and email
            dbsession = next(get_dbsession())  # Get the SQLAlchemy session
            user = (
                dbsession.query(AuthEntity)
                .filter_by(username=username, email=email)
                .one_or_none()
            )
            dbsession.close()

            if user and user.id != user_id:
                return JsonResponse(
                    {
                        "success": False,
                        "profile_form_invalid_error": "Username and email is being along with another user. Failed to update.",
                    }
                )

            # check user self
            dbsession = next(get_dbsession())  # Get the SQLAlchemy session
            user = dbsession.query(AuthEntity).filter_by(id=user_id).one_or_none()

            if user:
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.company = company
                user.phone = phone
                user.email = email

                dbsession.add(user)
                dbsession.commit()
                dbsession.refresh(user)
                dbsession.close()

                # user exists already
                return JsonResponse(
                    {
                        "success": True,
                    }
                )

            dbsession.close()
            return JsonResponse(
                {
                    "success": False,
                    "profile_form_invalid_error": "User not found. Failed to update.",
                }
            )
        else:
            # If the form is not valid, render the form with errors
            template = "scada/profile.html"
            profile_form = ProfileForm(request.POST, user_id=user_id)
            context = {
                "profile_form": profile_form,
            }
            return render(request, template, context)

    @staticmethod
    def is_admin(email):
        if email in ADMIN_EMAIL:
            return True
        else:
            return False
