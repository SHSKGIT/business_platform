from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.views import generic
from django.views import View

# from ..models.invoice import Invoice, InvoiceItem
# from ..forms.invoice import InvoiceForm, InvoiceItemForm

from datetime import datetime


#=======================================================================================================================
class HomeView(View):

    def get(self, request):
        template = 'bio/home.html'
        data_list = [{'company': 'Infogen Labs Inc.'}, {'company': 'Eastridge Workforce Solutions'}, {'company': 'Outlaw Automation Inc.'}, ]
        return render(request, template, context={'data_list': data_list})

