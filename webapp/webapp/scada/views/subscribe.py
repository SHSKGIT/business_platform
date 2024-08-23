from django.shortcuts import render, redirect, get_object_or_404

from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.views import generic
from django.views import View
from django.http import HttpResponse, JsonResponse

from ..sqlalchemy_setup import get_dbsession
from ..models.subscribe import Subscribe
from ..forms.contact import ContactForm
from ..forms.subscribe import SubscribeForm
from ..forms.sign_in import SignInForm

from .send_email import prepare_email
from datetime import datetime


# =======================================================================================================================
class SubscribeView(View):
    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        form = SubscribeForm(request.POST)

        if form.is_valid():
            dbsession = next(get_dbsession())  # Get the SQLAlchemy session
            try:
                first_name = form.cleaned_data["nlfirstname"]
                last_name = form.cleaned_data["nllastname"]
                company = form.cleaned_data["nlcompany"]
                phone = form.cleaned_data["nlphone"]
                email = form.cleaned_data["nlmail"]

                name = f"{first_name} {last_name}"

                # Create a new subscribe object
                new_subscribe = Subscribe(
                    first_name=first_name,
                    last_name=last_name,
                    company=company,
                    phone=phone,
                    email=email,
                )

                # Add to session and commit, take effect to db table.
                dbsession.add(new_subscribe)
                dbsession.commit()
                dbsession.refresh(new_subscribe)

                # Send email
                prepare_email(
                    type="subscribe",
                    name=name,
                    email=email,
                    new_subscribe=new_subscribe,
                )

                return JsonResponse(
                    {
                        "success": True,
                        "name": name,
                    }
                )
            except Exception as e:
                dbsession.rollback()
                raise e  # You may handle the error differently based on your requirements
            finally:
                dbsession.close()
        else:
            # If the form is not valid, render the form with errors
            template = "scada/home.html"
            subscribe_form = SubscribeForm(request.POST)
            sign_in_form = SignInForm(request.POST)
            contact_form = ContactForm(request.POST)
            context = {
                "contact_form": contact_form,
                "subscribe_form": subscribe_form,
                "sign_in_form": sign_in_form,
            }
            return render(request, template, context)
