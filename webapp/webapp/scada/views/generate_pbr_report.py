from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View
from django.templatetags.static import static

from ..sqlalchemy_setup import get_dbsession
from ..models.auth_entity import AuthEntity

from ..oracle_connection import fetch_one_from_oracle, fetch_all_from_oracle

from weasyprint import HTML
import tempfile

from datetime import datetime, timedelta

from django.conf import settings
import os
import math
import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np


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
        oil_bar_plot_image_path = PBRReportView.generate_bar_plot(
            oil_table_data, "oil", pbr_start_date, pbr_end_date
        )

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
                "oil_bar_plot_url": oil_bar_plot_image_path,
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
        os.remove(oil_bar_plot_image_path)

        return response

    @staticmethod
    def generate_oil_table_data(start_date, end_date):
        query = """
                    SELECT NAME FROM v$database
                """
        data = fetch_all_from_oracle(query)

        # Data to populate in the report
        data = [
            {
                "activity": "INVCL",
                "product": "OIL",
                "volume": "590.4",
                "adj_total": "(590.4)",
                "notes": "SUBTRACT",
                "plot_x_name": "INVCL",
                "adj_total_minus": "Y",
            },
            {
                "activity": "INVOP",
                "product": "OIL",
                "volume": "600.2",
                "adj_total": "(600.20)",
                "notes": "ADD",
                "plot_x_name": "INVOP",
            },
            {
                "activity": "LDINJ",
                "product": "OIL",
                "volume": "925.8",
                "adj_total": "(925.80)",
                "notes": "SUBTRACT",
                "plot_x_name": "LDINJ",
                "adj_total_minus": "Y",
            },
            {
                "activity": "LDINVCL",
                "product": "OIL",
                "volume": "114.5",
                "adj_total": "",
                "notes": "IGNORE",
                "plot_x_name": "LDINVCL",
            },
            {
                "activity": "LDINVOP",
                "product": "OIL",
                "volume": "121.2",
                "adj_total": "",
                "notes": "IGNORE",
                "plot_x_name": "LDINVOP",
            },
            {
                "activity": "LDREC",
                "product": "OIL",
                "volume": "932.5",
                "adj_total": "(932.50)",
                "notes": "ADD",
                "plot_x_name": "LDREC",
            },
            {
                "activity": "PROD",
                "product": "OIL",
                "volume": "15098.9",
                "adj_total": "(15098.90)",
                "notes": "ADD",
                "plot_x_name": "PROD",
            },
            {
                "activity": "REC",
                "product": "OIL",
                "volume": "426.6",
                "adj_total": "(426.60)",
                "notes": "ADD",
                "plot_x_name": "REC-OIL",
            },
            {
                "activity": "REC",
                "product": "C5-SP",
                "volume": "",
                "adj_total": "(805.60)",
                "notes": "ADD",
                "plot_x_name": "REC-CS",
            },
            {
                "activity": "ROYALTY",
                "product": "OIL",
                "volume": "2766.1",
                "adj_total": "",
                "notes": "IGNORE",
                "plot_x_name": "ROYALTY",
            },
            {
                "activity": "",
                "product": "",
                "volume": "",
                "adj_total": "",
                "notes": "",
                "plot_x_name": "",
            },
            {
                "activity": "DISP",
                "product": "OIL",
                "volume": "16347.6",
                "adj_total": "16347.6",
                "notes": "",
                "plot_x_name": "DISP",
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
    def generate_bar_plot(data, product, start_date, end_date):
        # Extract valid data
        activities = [row["plot_x_name"] for row in data]
        for row in data:
            if row["adj_total"]:
                row["adj_total"] = float(
                    row["adj_total"].replace("(", "").replace(")", "")
                )
            else:
                row["adj_total"] = float(0)

        adj_totals = [
            row["adj_total"] * -1 if "adj_total_minus" in row else row["adj_total"]
            for row in data
        ]

        # Determine colors based on adj_total values
        # colors = ["red" if total < 0 else "green" for total in adj_totals]
        colors = ["red" if "adj_total_minus" in row else "green" for row in data]
        # Ensure "DISP" is black
        if "DISP" in activities:
            disp_index = activities.index("DISP")
            colors[disp_index] = "black"

        # Plotting
        fig, ax = plt.subplots(figsize=(10, 6))
        x_positions = np.arange(len(activities))
        bar_width = 0.5
        bars = ax.bar(
            x_positions, adj_totals, color=colors, width=bar_width, align="edge"
        )

        ax.set_xticks(x_positions)

        # Place the x-axis at y=0
        ax.axhline(0, color="grey", linewidth=1)

        # ===============================================
        # Set y scale with step of 2000
        max_val = max(adj_totals)
        min_val = min(adj_totals)
        ax.set_yticks(
            np.arange(
                PBRReportView.nearest_multiple(min_val, 2000),
                PBRReportView.nearest_multiple(max_val, 2000) + 2000,
                2000,
            )
        )

        # Set the color for y-ticks and labels
        ax.tick_params(axis="y", colors="grey")

        # Remove x-axis labels and place them on top of each bar
        # ax.set_xticks([])
        for i, bar in enumerate(bars):
            # Determine the height for positioning
            height = bar.get_height()

            # Positioning activity names
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                PBRReportView.nearest_multiple(max_val, 2000),
                activities[i],
                ha="center",
                va="bottom",
                fontsize=10,
                color="grey",
            )

            if height < 0:  # If adj_total is negative
                # Position below the bar
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height - 300,  # Positioning the label below the bar
                    f"{adj_totals[i]:,.2f}",
                    ha="center",
                    va="top",  # Align to the top of the specified y position
                    fontsize=10,  # Font size for the activity labels
                    color="grey",
                )
            else:
                if adj_totals[i] != float(0):
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        height + 300,  # Slightly lower than the activity name
                        f"{adj_totals[i]:,.2f}",  # Formatting the total with commas and 2 decimal points
                        ha="center",
                        va="bottom",
                        fontsize=10,  # Font size for the adj_total values
                        color="grey",
                    )

        # Set the visibility of the x-axis label to false
        # ax.xaxis.set_visible(False)

        # Set y-axis label with LaTeX for superscript
        ax.set_ylabel(r"Total Volume (M$^3$)", fontsize=10, color="grey")

        # Set tick parameters for larger font size
        ax.tick_params(axis="y", labelsize=10)

        # Enable minor ticks explicitly
        # ax.minorticks_on()
        # ax.tick_params(axis="y", which="minor", left=False)
        # ax.tick_params(axis="x", which="minor", bottom=True)
        # Add vertical light grey gridlines (splitter) between bars
        ax.set_xticks(np.arange(len(activities)))  # Major ticks at bar positions
        ax.set_xticks(
            np.arange(0.75, len(activities), 1), minor=True
        )  # Minor ticks between bars

        ax.grid(
            True,
            which="minor",
            axis="x",
            color="grey",
            linestyle="--",
            linewidth=0.7,
        )  # Grey splitter lines

        # Move the y-axis to the right
        ax.set_xlim(left=-0.25)  # Move the x-axis limits to the left by 0.25
        ax.spines["left"].set_position(
            ("outward", 0)
        )  # Move the y-axis outward (to the right)

        # Remove the x-axis labels
        ax.set_xticks([])

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)

        # Adding an outer frame around the entire plot
        fig.patch.set_linewidth(1)
        fig.patch.set_edgecolor("grey")
        fig.patch.set_facecolor("white")  # Set face color for better contrast

        # Adjust the layout to create space for the outer frame
        # plt.subplots_adjust(left=0.1, right=0.9, top=0.85, bottom=0.2)

        # Set title
        plt.title(f"OIL BALANCE", color="grey", fontweight="bold", fontsize=16, pad=20)

        plt.tight_layout()  # Adjust layout to not cut off labels

        # Save the plot as an image file
        image_path = os.path.join(
            settings.STATIC_ROOT,
            f'scada/images/pbr_report_{product}_bar_plot_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.png',
        )
        plt.savefig(f"{image_path}")

        # plt.show()

        return image_path

    @staticmethod
    def nearest_multiple(value, multiple):
        if value >= 0:
            # Calculate the nearest negative multiple
            nearest = math.ceil(value / multiple) * multiple
            if nearest <= value:
                nearest += multiple
        else:
            # Calculate the nearest negative multiple
            nearest = math.floor(value / -multiple) * -multiple
            if nearest >= value:
                nearest -= multiple

        return nearest
