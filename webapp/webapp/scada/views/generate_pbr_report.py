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
    "report_css_url": os.path.join(settings.STATIC_ROOT, "scada/css/pbr_report.css"),
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

        report_filename = f"OED_PBR_REPORT({pbr_start_date}-{pbr_end_date}).pdf"
        report_template = "scada/pbr_report.html"
        report_title = f"Production Balance Report"

        user_id = int(request.GET.get("user_id"))
        # Query the database for the user
        dbsession = next(get_dbsession())  # Get the SQLAlchemy session
        user = dbsession.query(AuthEntity).filter_by(id=user_id).one_or_none()
        dbsession.close()

        oil_table_data = PBRReportView.generate_oil_table_data(
            datetime.strptime(pbr_start_date, "%Y-%m-%d"),
            datetime.strptime(pbr_end_date, "%Y-%m-%d"),
        )
        gas_table_data = PBRReportView.generate_gas_table_data(
            datetime.strptime(pbr_start_date, "%Y-%m-%d"),
            datetime.strptime(pbr_end_date, "%Y-%m-%d"),
        )
        water_table_data = PBRReportView.generate_water_table_data(
            datetime.strptime(pbr_start_date, "%Y-%m-%d"),
            datetime.strptime(pbr_end_date, "%Y-%m-%d"),
        )
        # bar_plot_image_path = PBRReportView.generate_bar_plot(data, month, year)

        STATIC_FILE_URLs.update(
            {
                "generated_date": datetime.now().strftime("%Y-%m-%d"),
                "generated_by": (
                    user.first_name.capitalize() + " " + user.last_name.capitalize()
                ),
                "start_date": pbr_start_date,
                "end_date": pbr_end_date,
                "report_title": report_title,
                "battery_code": pbr_battery_code,
                "oil_table_data": oil_table_data,
                "gas_table_data": gas_table_data,
                "water_table_data": water_table_data,
                # "scatter_plot_url": scatter_plot_image_path,
                # "line_plot_url": line_plot_image_path,
                # "bar_plot_url": bar_plot_image_path,
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
        # os.remove(scatter_plot_image_path)
        # os.remove(line_plot_image_path)
        # os.remove(bar_plot_image_path)

        return response

    @staticmethod
    def generate_oil_table_data(start_date, end_date):
        # Data to populate in the report
        data = [
            {
                "activity": "INVCL",
                "product": "OIL",
                "volume": "590.4",
                "adj_total": "(590.4)",
                "notes": "SUBTRACT",
            },
            {
                "activity": "INVOP",
                "product": "OIL",
                "volume": "600.2",
                "adj_total": "(600.20)",
                "notes": "ADD",
            },
            {
                "activity": "LDINJ",
                "product": "OIL",
                "volume": "925.8",
                "adj_total": "(925.80)",
                "notes": "SUBTRACT",
            },
            {
                "activity": "LDINVCL",
                "product": "OIL",
                "volume": "114.5",
                "adj_total": "",
                "notes": "IGNORE",
            },
            {
                "activity": "LDINVOP",
                "product": "OIL",
                "volume": "121.2",
                "adj_total": "",
                "notes": "IGNORE",
            },
            {
                "activity": "LDREC",
                "product": "OIL",
                "volume": "932.5",
                "adj_total": "(932.50)",
                "notes": "ADD",
            },
            {
                "activity": "PROD",
                "product": "OIL",
                "volume": "15098.9",
                "adj_total": "(15098.90)",
                "notes": "ADD",
            },
            {
                "activity": "REC",
                "product": "OIL",
                "volume": "426.6",
                "adj_total": "(426.60)",
                "notes": "ADD",
            },
            {
                "activity": "REC",
                "product": "C5-SP",
                "volume": "",
                "adj_total": "(805.60)",
                "notes": "ADD",
            },
            {
                "activity": "ROYALTY",
                "product": "OIL",
                "volume": "2766.1",
                "adj_total": "",
                "notes": "IGNORE",
            },
            {
                "activity": "",
                "product": "",
                "volume": "",
                "adj_total": "",
                "notes": "",
            },
            {
                "activity": "DISP",
                "product": "OIL",
                "volume": "16347.6",
                "adj_total": "16347.6",
                "notes": "",
            },
        ]

        return data

    @staticmethod
    def generate_gas_table_data(start_date, end_date):
        # Data to populate in the report
        data = [
            {
                "activity": "FLARE",
                "product": "GAS",
                "volume": "7",
                "adj_total": "(7.00)",
                "notes": "SUBTRACT",
            },
            {
                "activity": "FUEL",
                "product": "GAS",
                "volume": "405",
                "adj_total": "(405.00)",
                "notes": "SUBTRACT",
            },
            {
                "activity": "PROD",
                "product": "GAS",
                "volume": "20977.6",
                "adj_total": "(20977.60)",
                "notes": "ADD",
            },
            {
                "activity": "PURREC",
                "product": "GAS",
                "volume": "9.1",
                "adj_total": "(9.10)",
                "notes": "ADD",
            },
            {
                "activity": "REC",
                "product": "GAS",
                "volume": "2743.7",
                "adj_total": "(2743.70)",
                "notes": "ADD",
            },
            {
                "activity": "VENT",
                "product": "GAS",
                "volume": "19.2",
                "adj_total": "(19.20)",
                "notes": "SUBTRACT",
            },
            {
                "activity": "",
                "product": "",
                "volume": "",
                "adj_total": "",
                "notes": "",
            },
            {
                "activity": "DISP",
                "product": "GAS",
                "volume": "23299.2",
                "adj_total": "23299.2",
                "notes": "",
            },
        ]

        return data

    @staticmethod
    def generate_water_table_data(start_date, end_date):
        # Data to populate in the report
        data = [
            {
                "activity": "INVCL",
                "product": "WATER",
                "volume": "361.9",
                "adj_total": "(361.90)",
                "notes": "SUBTRACT",
            },
            {
                "activity": "INVOP",
                "product": "WATER",
                "volume": "342.1",
                "adj_total": "(342.10)",
                "notes": "ADD",
            },
            {
                "activity": "LDINJ",
                "product": "WATER",
                "volume": "154.5",
                "adj_total": "(154.50)",
                "notes": "SUBTRACT",
            },
            {
                "activity": "LDINVCL",
                "product": "WATER",
                "volume": "182221.2",
                "adj_total": "",
                "notes": "IGNORE",
            },
            {
                "activity": "LDINVOP",
                "product": "WATER",
                "volume": "184056.2",
                "adj_total": "",
                "notes": "IGNORE",
            },
            {
                "activity": "LDREC",
                "product": "WATER",
                "volume": "1989.5",
                "adj_total": "(1989.50)",
                "notes": "ADD",
            },
            {
                "activity": "PROD",
                "product": "WATER",
                "volume": "4510.3",
                "adj_total": "(4510.30)",
                "notes": "ADD",
            },
            {
                "activity": "REC",
                "product": "WATER",
                "volume": "132.1",
                "adj_total": "(132.10)",
                "notes": "ADD",
            },
            {
                "activity": "",
                "product": "",
                "volume": "",
                "adj_total": "",
                "notes": "",
            },
            {
                "activity": "DISP",
                "product": "WATER",
                "volume": "6457.6",
                "adj_total": "6457.6",
                "notes": "",
            },
        ]

        return data

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
            f'scada/images/pbr_report_bar_plot_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.png',
        )
        plt.savefig(f"{image_path}")

        # plt.show()

        return image_path
