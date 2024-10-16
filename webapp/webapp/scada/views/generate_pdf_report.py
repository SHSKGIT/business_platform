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
    "logo_url": os.path.join(
        settings.STATIC_ROOT, "scada/images/report_logo(backup).png"
    ),
}


class MonthlyReportView(View):
    @staticmethod
    def get(request):
        month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime(
            "%b"
        )  # ex: Aug
        if datetime.now().strftime("%m") == "01":  # January
            year = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y")
        else:
            year = datetime.now().strftime("%Y")  # ex: 2024

        report_filename = f"OED_{month}/{year}_report.pdf"
        report_template = "scada/report_template_1.html"
        report_title = f"{month}/{year} Report"

        start_date = (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1)
        end_date = datetime.now().replace(day=1) - timedelta(days=1)

        data = MonthlyReportView.generate_fake_data(start_date, end_date)
        scatter_plot_image_path = MonthlyReportView.generate_scatter_plot(
            data, month, year
        )
        line_plot_image_path = MonthlyReportView.generate_line_plot(data, month, year)
        bar_plot_image_path = MonthlyReportView.generate_bar_plot(data, month, year)

        user_id = int(request.GET.get("user_id"))
        # Query the database for the user
        dbsession = next(get_dbsession())  # Get the SQLAlchemy session
        user = dbsession.query(AuthEntity).filter_by(id=user_id).one_or_none()
        dbsession.close()

        STATIC_FILE_URLs.update(
            {
                "generated_date": datetime.now().strftime("%Y-%m-%d"),
                "generated_by": " ".join(
                    [word.capitalize() for word in user.username.split(" ")]
                ),
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "report_title": report_title,
                "report_data": data,
                "scatter_plot_url": scatter_plot_image_path,
                "line_plot_url": line_plot_image_path,
                "bar_plot_url": bar_plot_image_path,
            }
        )

        # Render the HTML template with the report data
        html_string = render_to_string(report_template, STATIC_FILE_URLs)

        # Convert the HTML string to a PDF
        html = HTML(string=html_string, base_url=request.build_absolute_uri("/"))
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f"inline; filename={report_filename}"

        # Write the PDF to the response
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            html.write_pdf(target=temp_file.name)
            response.write(temp_file.read())

        # remove scatter plot image file to save space
        os.remove(scatter_plot_image_path)
        os.remove(line_plot_image_path)
        os.remove(bar_plot_image_path)

        return response

    @staticmethod
    def generate_fake_data(start_date, end_date):
        # Data to populate in the report
        fake_data = []
        for r in range(start_date.day, end_date.day + 1)[::-1]:
            min_value = 1.0
            max_value = 10.0
            fake_data.append(
                {
                    "Date": (end_date - timedelta(r - 1)).strftime("%Y-%m-%d"),
                    "Oil": round(random.uniform(min_value, max_value), 3),
                    "Condy": round(random.uniform(min_value, max_value), 3),
                    "Water": round(random.uniform(min_value, max_value), 3),
                }
            )

        return fake_data

    @staticmethod
    def generate_scatter_plot(data, month, year):
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df["Date"] = pd.to_datetime(df["Date"])  # Convert the 'Date' column to datetime

        # Plotting
        fig, ax = plt.subplots(figsize=(30, 15))

        # Plot each variable
        ax.scatter(df["Date"], df["Oil"], color="r", label="Oil", s=1)
        ax.scatter(df["Date"], df["Condy"], color="g", label="Condy", s=1)
        ax.scatter(df["Date"], df["Water"], color="b", label="Water", s=1)

        # Set x-axis limits to match the data range
        ax.set_xlim(df["Date"].min(), df["Date"].max())

        # Format date on x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(mdates.DayLocator())
        fig.autofmt_xdate()  # Auto-format the date labels to prevent overlap

        # Customize plot
        ax.set_xlabel("Date")
        ax.set_ylabel("Values")
        ax.set_title(f"Scatter Plot of Oil, Condy, and Water in {month}/{year}")
        ax.legend()

        # Add labels for each point
        for i in range(len(df)):
            # Oil points
            ax.text(
                df["Date"].iloc[i],
                df["Oil"].iloc[i],
                f'{df["Oil"].iloc[i]}',
                fontsize=10,
                color="r",
                ha="left",
            )

            # Condy points
            ax.text(
                df["Date"].iloc[i],
                df["Condy"].iloc[i],
                f'{df["Condy"].iloc[i]}',
                fontsize=10,
                color="g",
                ha="left",
            )

            # Water points
            ax.text(
                df["Date"].iloc[i],
                df["Water"].iloc[i],
                f'{df["Water"].iloc[i]}',
                fontsize=10,
                color="b",
                ha="left",
            )

        # Rotate and format the x-axis labels
        plt.xticks(rotation=45)
        plt.tight_layout()  # Adjust layout to not cut off labels

        # Save the plot as an image file
        image_path = os.path.join(
            settings.STATIC_ROOT,
            f'scada/images/scatter_plot_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.png',
        )
        plt.savefig(f"{image_path}")

        # plt.show()

        return image_path

    @staticmethod
    def generate_line_plot(data, month, year):
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df["Date"] = pd.to_datetime(df["Date"])  # Convert the 'Date' column to datetime

        # Plotting
        fig, ax = plt.subplots(figsize=(30, 15))

        # Line plot
        ax.plot(
            df["Date"],
            df["Oil"],
            color="r",
            label="Oil",
            marker="o",
            markersize=1,
            linestyle="-",
        )
        ax.plot(
            df["Date"],
            df["Condy"],
            color="g",
            label="Condy",
            marker="s",
            markersize=1,
            linestyle="-",
        )
        ax.plot(
            df["Date"],
            df["Water"],
            color="b",
            label="Water",
            marker="s",
            markersize=1,
            linestyle="-",
        )

        # Set x-axis limits to match the data range
        ax.set_xlim(df["Date"].min(), df["Date"].max())

        # Format date on x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(mdates.DayLocator())
        fig.autofmt_xdate()  # Auto-format the date labels to prevent overlap

        # Customize plot
        ax.set_xlabel("Date")
        ax.set_ylabel("Values")
        ax.set_title(f"Line Plot of Oil, Condy, and Water in {month}/{year}")
        ax.legend()

        # Add labels for each point
        for i in range(len(df)):
            # Oil points
            ax.text(
                df["Date"].iloc[i],
                df["Oil"].iloc[i],
                f'{df["Oil"].iloc[i]}',
                fontsize=10,
                color="r",
                ha="left",
            )

            # Condy points
            ax.text(
                df["Date"].iloc[i],
                df["Condy"].iloc[i],
                f'{df["Condy"].iloc[i]}',
                fontsize=10,
                color="g",
                ha="left",
            )

            # Water points
            ax.text(
                df["Date"].iloc[i],
                df["Water"].iloc[i],
                f'{df["Water"].iloc[i]}',
                fontsize=10,
                color="b",
                ha="left",
            )

        # Rotate and format the x-axis labels
        plt.xticks(rotation=45)
        plt.tight_layout()  # Adjust layout to not cut off labels

        # Save the plot as an image file
        image_path = os.path.join(
            settings.STATIC_ROOT,
            f'scada/images/line_plot_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.png',
        )
        plt.savefig(f"{image_path}")

        # plt.show()

        return image_path

    @staticmethod
    def generate_bar_plot(data, month, year):
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df["Date"] = pd.to_datetime(df["Date"])  # Convert the 'Date' column to datetime

        # Plotting
        fig, ax = plt.subplots(figsize=(30, 15))

        # Bar width
        bar_width = 0.25

        # Plot each variable
        ax.bar(
            df["Date"],
            df["Oil"],
            color="r",
            width=bar_width,
            edgecolor="black",
            label="Oil",
        )
        ax.bar(
            df["Date"],
            df["Condy"],
            color="g",
            width=bar_width,
            edgecolor="black",
            label="Condy",
        )
        ax.bar(
            df["Date"],
            df["Water"],
            color="b",
            width=bar_width,
            edgecolor="black",
            label="Water",
        )

        # Set x-axis limits to match the data range
        ax.set_xlim(df["Date"].min(), df["Date"].max())

        # Format date on x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(mdates.DayLocator())
        fig.autofmt_xdate()  # Auto-format the date labels to prevent overlap

        # Customize plot
        ax.set_xlabel("Date")
        ax.set_ylabel("Values")
        ax.set_title(f"Bar Plot of Oil, Condy, and Water in {month}/{year}")
        ax.legend()

        # Add labels for each point
        for i in range(len(df)):
            # Oil points
            ax.text(
                df["Date"].iloc[i],
                df["Oil"].iloc[i],
                f'{df["Oil"].iloc[i]}',
                fontsize=10,
                color="r",
                ha="left",
            )

            # Condy points
            ax.text(
                df["Date"].iloc[i],
                df["Condy"].iloc[i],
                f'{df["Condy"].iloc[i]}',
                fontsize=10,
                color="g",
                ha="left",
            )

            # Water points
            ax.text(
                df["Date"].iloc[i],
                df["Water"].iloc[i],
                f'{df["Water"].iloc[i]}',
                fontsize=10,
                color="b",
                ha="left",
            )

        # Rotate and format the x-axis labels
        plt.xticks(rotation=45)
        plt.tight_layout()  # Adjust layout to not cut off labels

        # Save the plot as an image file
        image_path = os.path.join(
            settings.STATIC_ROOT,
            f'scada/images/bar_plot_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.png',
        )
        plt.savefig(f"{image_path}")

        # plt.show()

        return image_path


class GeneralReportView(View):
    @staticmethod
    def get(request):
        report_filename = f"OED_agreement_report.pdf"
        report_template = "scada/report_template_2.html"
        report_title = f"OED Agreement Report"

        base_data = STATIC_FILE_URLs | {
            "report_filename": report_filename,
            "report_template": report_template,
            "report_title": report_title,
            "generated_date": datetime.now().strftime("%Y-%m-%d"),
        }

        all_data = GeneralReportView.generate_fake_data(base_data)

        # Render the HTML template with the report data
        html_string = render_to_string(report_template, all_data)

        # Convert the HTML string to a PDF
        html = HTML(string=html_string, base_url=request.build_absolute_uri("/"))
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f"inline; filename={report_filename}"

        # Write the PDF to the response
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            html.write_pdf(target=temp_file.name)
            response.write(temp_file.read())

        return response

    @staticmethod
    def generate_fake_data(base_data):
        # Data to populate in the report
        general_data = {
            "agreement_type": "OIL SANDS LEASE",
            "agreement_number": "075 7595120071",
            "status": "ACTIVE",
            "designated_representative": "CONOCOPHILLIPS CANADA RESOURCES CORP. (ACTIVE 1001181 002)",
            "current_area": "17,202.16",
            "original_area": "17,169.20",
            "term": "15 Years 0 Months 0 Days",
            "rental_amount": "60,207.56",
            "rental_paid_to": "December 02, 2024",
            "monthly_invoice": "Yes",
            "rental_default_notice": "No",
            "original_payment": "0.00",
            "security_type": "",
            "offset_compensation": "No",
            "encumbrance_count": "0",
            "well_count": "940",
            "cancellation": "",
            "term_date": "December 02, 1995",
            "original_expiry_date": "December 02, 2010",
            "current_expiry_date": "",
            "vintage": "CONTINUED",
            "continuation_pending": "No",
            "continuation_date": "December 02, 2010",
            "transfer_pending": "No",
            "sale_or_oc_date": "",
            "payment_origin": "",
            "security_deposit_amount": "0.00",
            "last_transfer_date": "November 09, 2023",
            "last_update_date": "November 28, 2023",
            "oil_sands_area": "OIL SANDS AREA 1 - ATHABASCA - PETROLEUM IS DEEMED TO BE OIL SANDS BETWEEN THE TOP OF THE VIKING FORMATION AND THE BASE OF THE WOODBEND GROUP",
        }

        report_participant_data = {
            "report_participant_data": [
                {
                    "client_id": "1001181",
                    "client_name": "CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "client_status": "ACTIVE",
                    "interest": "100.0000000",
                },
            ]
        }

        land_rights_data = {
            "land_update_flag": "No",
            "land_rights_data": [
                {
                    "lands_rights": "00 4-05-082: 19; 20; 21; 28; 29; 30; 31; 32; 33 (ROAD WEST)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;OIL SANDS<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BELOW THE TOP OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TO THE BASE OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;as designated in DRRZR Z2814<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Key Well: 00/10-20-082-06W4/00<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Interval: 724.00 - 954.00 Feet (Zone: WABISKAW-MCMURRAY)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Log Type: LATEROLOG",
                    "area": "76.80",
                    "section_of_act": "13",
                    "continued_to": "INDEFINITE",
                },
                {
                    "lands_rights": "00 4-05-082: 19; 20; 21; 28; 29; 30; 31; 32; 33<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;OIL SANDS<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BELOW THE TOP OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TO THE BASE OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;as designated in DRRZR Z2814<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Key Well: 00/10-20-082-06W4/00<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Interval: 724.00 - 954.00 Feet (Zone: WABISKAW-MCMURRAY)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Log Type: LATEROLOG",
                    "area": "4,608.00",
                    "section_of_act": "13",
                    "continued_to": "INDEFINITE",
                },
                {
                    "lands_rights": "00 4-05-082: 28; 29; 30 (ROAD INTERSECTION)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;OIL SANDS<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BELOW THE TOP OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TO THE BASE OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;as designated in DRRZR Z2814<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Key Well: 00/10-20-082-06W4/00<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Interval: 724.00 - 954.00 Feet (Zone: WABISKAW-MCMURRAY)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Log Type: LATEROLOG",
                    "area": "0.48",
                    "section_of_act": "13",
                    "continued_to": "INDEFINITE",
                },
                {
                    "lands_rights": "00 4-05-082: 28; 29; 30 (ROAD SOUTH)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;OIL SANDS<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BELOW THE TOP OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TO THE BASE OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;as designated in DRRZR Z2814<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Key Well: 00/10-20-082-06W4/00<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Interval: 724.00 - 954.00 Feet (Zone: WABISKAW-MCMURRAY)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Log Type: LATEROLOG",
                    "area": "28.80",
                    "section_of_act": "13",
                    "continued_to": "INDEFINITE",
                },
                {
                    "lands_rights": "00 4-05-083: 04; 05; 06; 07; 08; 09; 16; 17; 18<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;OIL SANDS<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BELOW THE TOP OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TO THE BASE OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;as designated in DRRZR Z2814<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Key Well: 00/10-20-082-06W4/00<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Interval: 724.00 - 954.00 Feet (Zone: WABISKAW-MCMURRAY)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Log Type: LATEROLOG",
                    "area": "4,608.00",
                    "section_of_act": "13",
                    "continued_to": "INDEFINITE",
                },
                {
                    "lands_rights": "00 4-05-083: 04; 05; 06; 07; 08; 09; 16; 17; 18 (ROAD WEST)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;OIL SANDS<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BELOW THE TOP OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TO THE BASE OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;as designated in DRRZR Z2814<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Key Well: 00/10-20-082-06W4/00<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Interval: 724.00 - 954.00 Feet (Zone: WABISKAW-MCMURRAY)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Log Type: LATEROLOG",
                    "area": "76.80",
                    "section_of_act": "13",
                    "continued_to": "INDEFINITE",
                },
                {
                    "lands_rights": "00 4-05-083: 04; 05; 06; 16; 17; 18 (ROAD SOUTH)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;OIL SANDS<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BELOW THE TOP OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TO THE BASE OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;as designated in DRRZR Z2814<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Key Well: 00/10-20-082-06W4/00<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Interval: 724.00 - 954.00 Feet (Zone: WABISKAW-MCMURRAY)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Log Type: LATEROLOG",
                    "area": "56.00",
                    "section_of_act": "13",
                    "continued_to": "INDEFINITE",
                },
                {
                    "lands_rights": "00 4-05-083: 04; 05; 06; 16; 17; 18 (ROAD INTERSECTION)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;OIL SANDS<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BELOW THE TOP OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TO THE BASE OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;as designated in DRRZR Z2814<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Key Well: 00/10-20-082-06W4/00<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Interval: 724.00 - 954.00 Feet (Zone: WABISKAW-MCMURRAY)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Log Type: LATEROLOG",
                    "area": "0.96",
                    "section_of_act": "13",
                    "continued_to": "INDEFINITE",
                },
                {
                    "lands_rights": "00 4-06-082: 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 19; 20; 21; 22; 23; 24; 25; 26; 27; 28; 29;<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;OIL SANDS<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BELOW THE TOP OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TO THE BASE OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;as designated in DRRZR Z2814<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Key Well: 00/10-20-082-06W4/00<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Interval: 724.00 - 954.00 Feet (Zone: WABISKAW-MCMURRAY)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Log Type: LATEROLOG",
                    "area": "15,360.00",
                    "section_of_act": "13",
                    "continued_to": "INDEFINITE",
                },
                {
                    "lands_rights": "00 4-06-082: 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 20; 21; 22; 23; 24; 25; 26; 27; 28; 29; 32; 33; 34;<br> \
                                            &nbsp;&nbsp;&nbsp;&nbsp;OIL SANDS<br> \
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BELOW THE TOP OF THE WABISKAW-MCMURRAY<br> \
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TO THE BASE OF THE WABISKAW-MCMURRAY<br> \
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;as designated in DRRZR Z2814<br> \
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Key Well: 00/10-20-082-06W4/00<br> \
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Interval: 724.00 - 954.00 Feet (Zone: WABISKAW-MCMURRAY)<br> \
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Log Type: LATEROLOG",
                    "area": "160.00",
                    "section_of_act": "13",
                    "continued_to": "INDEFINITE",
                },
                {
                    "lands_rights": "00 4-06-082: 13; 14; 15; 16; 17; 18; 25; 26; 27; 28; 29; 30 (ROAD SOUTH)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;OIL SANDS<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BELOW THE TOP OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TO THE BASE OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;as designated in DRRZR Z2814<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Key Well: 00/10-20-082-06W4/00<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Interval: 724.00 - 954.00 Feet (Zone: WABISKAW-MCMURRAY)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Log Type: LATEROLOG",
                    "area": "76.80",
                    "section_of_act": "13",
                    "continued_to": "INDEFINITE",
                },
                {
                    "lands_rights": "00 4-06-082: 13; 14; 15; 16; 17; 25; 26; 27; 28; 29 (ROAD INTERSECTION)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;OIL SANDS<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BELOW THE TOP OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TO THE BASE OF THE WABISKAW-MCMURRAY<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;as designated in DRRZR Z2814<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Key Well: 00/10-20-082-06W4/00<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Interval: 724.00 - 954.00 Feet (Zone: WABISKAW-MCMURRAY)<br> \
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Log Type: LATEROLOG",
                    "area": "0.80",
                    "section_of_act": "13",
                    "continued_to": "INDEFINITE",
                },
            ],
        }

        well_events_data = {
            "well_events_data": [
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-04-083-05W4/00",
                    "license_number": "0371926 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-09-083-05W4/00",
                    "license_number": "0453835 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-22-083-06W4/00",
                    "license_number": "0348909 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012208306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-23-083-06W4/00",
                    "license_number": "0473686 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-25-082-06W4/00",
                    "license_number": "0441585 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA012508206W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-27-083-06W4/00",
                    "license_number": "0429080 (ISSUED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/01-34-083-06W4/00",
                    "license_number": "0348285 (AMENDED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP. <strong>Previous UWI:</strong> 1AA013408306W400",
                    "well_event_status": "",
                },
                {
                    "well_events": "100/02-12-083-06W4/00",
                    "license_number": "0452945 (ABANDONED)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "ABANDONED",
                },
                {
                    "well_events": "100/02-13-083-06W4/00",
                    "license_number": "0477951 (SUSPENSION)",
                    "delimiter": "OIL SANDS WELL<br><strong>Licensee:</strong> CONOCOPHILLIPS CANADA RESOURCES CORP.",
                    "well_event_status": "",
                },
            ]
        }

        related_agreements_data = {
            "related_agreements_data": [
                {
                    "related_agreements": "RENEWAL INTO ",
                    "date": "Dec 02, 1995",
                    "agreement_id": "071 7174120071",
                    "status": "CANCELLED",
                    "area": "17,169.20",
                    "cancellation": "RENEWAL(Dec 02, 1995)",
                },
                {
                    "related_agreements": "AMENDMENT - OTHER - LAND ",
                    "date": "Dec 02, 1995",
                    "agreement_id": "",
                    "status": "",
                    "area": "0.16",
                    "cancellation": "",
                },
                {
                    "related_agreements": "AMENDMENT - OTHER - LAND ",
                    "date": "Jul 21, 2015",
                    "agreement_id": "",
                    "status": "",
                    "area": "33.12",
                    "cancellation": "",
                },
            ]
        }

        crown_mineral_activities_data = {
            "crown_mineral_activities_data": [
                {
                    "crown_mineral_activities": "WELL RE-ENTRY<br> \
                                                &nbsp;&nbsp;&nbsp;&nbsp;<strong>Wells:</strong> 100071508306W400, 100071508306W400",
                    "status": "CANCELLED",
                    "activity_id": "13070136",
                    "approval_date": "Jul 04, 2013",
                    "expiry_date": "Sep 04, 2013",
                    "cancellation": "Sep 04, 2013 (EXPIRED-NO LICENCE)",
                },
                {
                    "crown_mineral_activities": "WELL OVER HOLE<br> \
                                                &nbsp;&nbsp;&nbsp;&nbsp;<strong>Wells:</strong> 1AA061108307W400, 1AA081008307W400, 1AA160208307W400, 1AB051208306W400, 1AB060608306W400, 1AB141208306W400, 1AB150208307W400",
                    "status": "REJECTED",
                    "activity_id": "16070328",
                    "approval_date": "Jul 19, 2016",
                    "expiry_date": "Jul 19, 2017",
                    "cancellation": "Sep 18, 2024",
                },
                {
                    "crown_mineral_activities": "WELL OVER HOLE<br> \
                                                &nbsp;&nbsp;&nbsp;&nbsp;<strong>Wells:</strong> 100081308306W400, 100151208306W400, 1AA020208307W400, 1AA041308307W400, 1AA070208307W400, 1AA101108307W400, \
                                                1AA141208307W400, 1AA161008307W400, 1AB031408307W400, 1AB040708306W400, 1AB061308306W400, 1AB071408307W400, \
                                                1AB081508307W400, 1AB091108307W400, 1AB130608306W400, 1AB131108307W400, 1AB141008307W400",
                    "status": "REJECTED",
                    "activity_id": "16070329",
                    "approval_date": "Jul 20, 2016",
                    "expiry_date": "Jul 20, 2017",
                    "cancellation": "Sep 18, 2024",
                },
            ]
        }

        global_metes_and_bounds_data = {
            "global_metes_and_bounds_data": [
                {
                    "global_metes_and_bounds": """<strong>1</strong> AND ALL STATUTORY ROAD ALLOWANCES AND WHAT WOULD BE STATUTORY ROAD ALLOWANCES IF THE LANDS WERE SURVEYED
                                            PURSUANT TO THE SURVEYS ACT, LYING WITHIN THE OUTER LIMITS OF THE ABOVE DESCRIBED LANDS
                                            """,
                },
            ]
        }

        special_provisions_data = {
            "special_provisions_data": [
                {
                    "special_provisions": """<strong>1</strong> THESE OIL SANDS RIGHTS ARE SUBJECT TO THE MEMORANDUM OF AGREEMENT AUTHORIZED BY ORDER IN COUNCIL 83/2002 DATED
                                            FEBRUARY 27, 2002 AND THE REIMBURSEMENT AGREEMENT AUTHORIZED BY ORDER IN COUNCIL 251/2002 DATED MAY 29, 2002 (THE
                                            "AGREEMENTS"), AND ALL THE PROVISIONS, TERMS AND CONDITIONS CONTAINED THEREIN. ANY PARTY PURCHASING THESE OIL SANDS
                                            RIGHTS, IF IT IS NOT ALREADY A PARTY TO THE AGREEMENTS, MUST BECOME A PARTY TO THE AGREEMENTS AND MUST ASSUME ALL
                                            OBLIGATIONS UNDER THE AGREEMENTS. THE CROWN RESERVES THE RIGHT TO WITHHOLD THE REGISTRATION OF ANY TRANSFER OF
                                            THESE OILS SANDS RIGHTS UNTIL THE PURCHASER BECOMES A PARTY TO THE AGREEMENTS. THESE OIL SANDS RIGHTS MAY CEASE TO
                                            BE SUBJECT TO THE REIMBURSEMENT AGREEMENT IF CONSTRUCTION OF THE BITUMEN PROJECT COMMENCES, OR COMMERCIAL
                                            PRODUCTION FROM THE BITUMEN PROJECT IS ACHIEVED, BY THE DATES SPECIFIED IN ARTICLE 6 OF THE REIMBURSEMENT
                                            AGREEMENT.\" \"
                                            """,
                },
            ]
        }

        disclaimer_data = {
            "disclaimer_data": [
                {
                    "disclaimer": """This Search/Report is provided on the condition and understanding that One Energy Data is in no way responsible for loss or damage arising from any errors or
                                    omissions in this search/report and any person making use of or relying on this search/report herby releases One Energy Data or its owners from any and all
                                    liability for such loss or damage. <strong>Contact Us:</strong> <a href="mailto:info@OneEnergyData.com">info@OneEnergyData.com</a>
                                    """,
                },
            ]
        }

        return (
            base_data
            | general_data
            | report_participant_data
            | land_rights_data
            | well_events_data
            | related_agreements_data
            | crown_mineral_activities_data
            | global_metes_and_bounds_data
            | special_provisions_data
            | disclaimer_data
        )
