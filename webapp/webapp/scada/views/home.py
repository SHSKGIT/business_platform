from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.views import generic
from django.views import View

# from ..models.invoice import Invoice, InvoiceItem
from ..forms.contact import ContactForm
from ..forms.subscribe import SubscribeForm
from ..forms.sign_in import SignInForm

from datetime import datetime


# =======================================================================================================================
class HomeView(View):
    @staticmethod
    def get(request):
        template = "scada/home.html"
        contact_form = ContactForm()
        subscribe_form = SubscribeForm()
        sign_in_form = SignInForm()
        context = {
            "contact_form": contact_form,
            "subscribe_form": subscribe_form,
            "sign_in_form": sign_in_form,
        }

        return render(request, template, context)


# =======================================================================================================================
def _flt(v, dflt=0.0):
    try:
        return float(v)
    except:
        return dflt


def _int(v, dflt=0):
    try:
        return int(v)
    except:
        return dflt
