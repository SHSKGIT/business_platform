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
        data = {
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
                {
                    "client_id": "1001182",
                    "client_name": "CNRL",
                    "client_status": "ACTIVE",
                    "interest": "101.0000000",
                },
                {
                    "client_id": "1001183",
                    "client_name": "TC Energy",
                    "client_status": "ACTIVE",
                    "interest": "102.0000000",
                },
                {
                    "client_id": "1001184",
                    "client_name": "Suncor Energy",
                    "client_status": "ACTIVE",
                    "interest": "103.0000000",
                },
            ]
        }

        return data | report_participant_data | base_data
