from django.shortcuts import render, redirect, get_object_or_404

from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.views import generic
from django.views import View
from django.http import HttpResponse, JsonResponse

from ..sqlalchemy_setup import get_dbsession
from ..models.contact import Contact
from ..forms.contact import ContactForm
from ..forms.subscribe import SubscribeForm
from ..forms.sign_in import SignInForm


from .send_email import prepare_email
from datetime import datetime


# =======================================================================================================================
class ContactView(View):
    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            dbsession = next(get_dbsession())  # Get the SQLAlchemy session
            try:
                name = contact_form.cleaned_data["name"]
                email = contact_form.cleaned_data["email"]
                comment = contact_form.cleaned_data["comment"]
                # Create a new contact object
                new_contact = Contact(name=name, email=email, comment=comment)

                # Add to session and commit, take effect to db table.
                dbsession.add(new_contact)
                dbsession.commit()
                dbsession.refresh(new_contact)

                # Send email
                prepare_email(
                    type="contact",
                    name=name,
                    email=email,
                    comment=comment,
                    new_contact=new_contact,
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
            context = {
                "contact_form": contact_form,
                "subscribe_form": subscribe_form,
                "sign_in_form": sign_in_form,
            }
            return render(request, template, context)
