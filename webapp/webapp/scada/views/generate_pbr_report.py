from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View
from django.templatetags.static import static

from ..sqlalchemy_setup import get_dbsession
from ..models.auth_entity import AuthEntity

from weasyprint import HTML
import tempfile

from datetime import datetime, timedelta

from django.conf import settings
import os
import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd


STATIC_FILE_URLs = {
    # "report_js_url": os.path.join(settings.STATIC_ROOT, "scada/js/report.js"),  # javascript doesn't work with WeasyPrint
    "report_css_url": os.path.join(settings.STATIC_ROOT, "scada/css/report.css"),
    "bootstrap_css_url": os.path.join(settings.STATIC_ROOT, "scada/css/bootstrap.css"),
    "bootstrap_responsive_css_url": os.path.join(
        settings.STATIC_ROOT, "scada/css/bootstrap-responsive.css"
    ),
    "style_css_url": os.path.join(settings.STATIC_ROOT, "scada/css/style.css"),
    "pluton_css_url": os.path.join(settings.STATIC_ROOT, "scada/css/pluton.css"),
    "pluton_ie7_css_url": os.path.join(
        settings.STATIC_ROOT, "scada/css/pluton-ie7.css"
    ),
    "cslider_css_url": os.path.join(
        settings.STATIC_ROOT, "scada/css/jquery.cslider.css"
    ),
    "bxslider_css_url": os.path.join(
        settings.STATIC_ROOT, "scada/css/jquery.bxslider.css"
    ),
    "animate_css_url": os.path.join(settings.STATIC_ROOT, "scada/css/animate.css"),
    "logo_url": os.path.join(settings.STATIC_ROOT, "scada/images/report_logo.png"),
}


class PBRReportView(View):
    @staticmethod
    def get(request):
        user_id = request.GET.get("user_id")
        pbr_battery_code = request.GET.get("pbr_battery_code")
        pbr_start_date = request.GET.get("pbr_start_date")
        pbr_end_date = request.GET.get("pbr_end_date")
