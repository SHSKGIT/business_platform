from django.template.loader import render_to_string
from django.views import View
from django.templatetags.static import static
from django.http import HttpResponse, JsonResponse

from ..sqlalchemy_setup import get_dbsession
from ..models.auth_entity import AuthEntity

from ..oracle_connection import fetch_one_from_oracle, fetch_all_from_oracle

from weasyprint import HTML
import tempfile

from datetime import datetime, timedelta

from django.conf import settings
import os
import io
import math
import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from decimal import Decimal
from base64 import b64encode


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
        pbr_battery_code_list = pbr_battery_code.split(",")
        pbr_battery_code_string = ", ".join(pbr_battery_code_list)
        pbr_start_date = request.GET.get("pbr_start_date")
        pbr_end_date = request.GET.get("pbr_end_date")
        unit = request.GET.get("unit")

        if not PBRReportView.check_facility_id(pbr_battery_code_string):
            return JsonResponse(
                {
                    "success": True,
                    "facility_id_available": False,
                    "error": "Facility ID is not available. Please check your typing.",
                }
            )

        report_filename = f"OED_PBR_REPORT({pbr_start_date}-{pbr_end_date}).pdf"
        report_template = "scada/pbr_report.html"
        report_title = f"Production Balance Report"

        # Query the database for the user
        dbsession = next(get_dbsession())  # Get the SQLAlchemy session
        user = dbsession.query(AuthEntity).filter_by(id=int(user_id)).one_or_none()
        dbsession.close()

        oil_table_data = PBRReportView.generate_oil_table_data(
            pbr_battery_code_string,
            pbr_start_date,
            pbr_end_date,
            unit,
            1.0 if unit == "metric" else 6.28981,
        )
        gas_table_data = PBRReportView.generate_gas_table_data(
            pbr_battery_code_string,
            pbr_start_date,
            pbr_end_date,
            unit,
            1.0 if unit == "metric" else 0.035314666721488586,
        )
        water_table_data = PBRReportView.generate_water_table_data(
            pbr_battery_code_string,
            pbr_start_date,
            pbr_end_date,
            unit,
            1.0 if unit == "metric" else 6.28981,
        )

        oil_bar_plot_image_path = PBRReportView.generate_bar_plot(
            oil_table_data,
            "oil",
            pbr_start_date,
            pbr_end_date,
            unit,
            1.0 if unit == "metric" else 6.28981,
        )
        gas_bar_plot_image_path = PBRReportView.generate_bar_plot(
            gas_table_data,
            "gas",
            pbr_start_date,
            pbr_end_date,
            unit,
            1.0 if unit == "metric" else 0.035314666721488586,
        )
        water_bar_plot_image_path = PBRReportView.generate_bar_plot(
            water_table_data,
            "water",
            pbr_start_date,
            pbr_end_date,
            unit,
            1.0 if unit == "metric" else 6.28981,
        )

        # Convert the in-memory images to base64 strings
        oil_image_base64 = b64encode(oil_bar_plot_image_path.getvalue()).decode("utf-8")
        gas_image_base64 = b64encode(gas_bar_plot_image_path.getvalue()).decode("utf-8")
        water_image_base64 = b64encode(water_bar_plot_image_path.getvalue()).decode(
            "utf-8"
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
                "oil_bar_plot_url": f"data:image/png;base64,{oil_image_base64}",
                "gas_bar_plot_url": f"data:image/png;base64,{gas_image_base64}",
                "water_bar_plot_url": f"data:image/png;base64,{water_image_base64}",
                "unit": unit.capitalize(),
            }
        )

        # Render the HTML template with the report data
        html_string = render_to_string(report_template, STATIC_FILE_URLs)

        # Convert the HTML string to a PDF
        html = HTML(string=html_string, base_url=request.build_absolute_uri("/"))
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f"inline; filename={report_filename}"
        response["facility_id_available"] = True  # Optional header

        # Write the PDF to the response
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            html.write_pdf(target=temp_file.name)
            temp_file.seek(0)  # Ensure the pointer is at the beginning
            response.write(temp_file.read())

        return response

    @staticmethod
    def check_facility_id(pbr_battery_code):
        query = f"""
                    SELECT DISTINCT FACILITY_ID as facility_id,
                            COUNT(FACILITY_ID)
                    FROM PETRINEX_VOLUMETRIC_DATA
                    WHERE lower(FACILITY_ID)=lower('{pbr_battery_code}')
                    GROUP BY FACILITY_ID
                    ORDER BY FACILITY_ID ASC
                """
        db_data = fetch_all_from_oracle(query)
        if db_data and len(db_data) == 1:
            return True

        return False

    @staticmethod
    def convert_from_metric_to_imperial(data):
        return data

    @staticmethod
    def generate_oil_table_data(pbr_battery_code, start_date, end_date, unit, rate):
        query = f"""
                    SELECT ACTIVITY_ID, 
                            PRODUCT_ID,
                            SUM(TO_NUMBER(REPLACE(VOLUME, '.', '')) / POWER(10, LENGTH(SUBSTR(VOLUME, INSTR(VOLUME, '.'))) - 1) * {rate}) AS total_volume
                    FROM PETRINEX_VOLUMETRIC_DATA
                    WHERE PRODUCT_ID IN ('OIL', 'C5-SP')
                        AND FACILITY_ID in ('{pbr_battery_code}')
                        AND ACTIVITY_ID IN ('INVCL', 'INVOP', 'LDINJ', 'LDINVCL', 'LDINVOP', 'LDREC', 'PROD', 'REC', 'ROYALTY', 'DISP') 
                        AND PRODUCTION_MONTH BETWEEN TO_DATE('{start_date}', 'YYYY-MM-DD') AND TO_DATE('{end_date}', 'YYYY-MM-DD')
                    GROUP BY ACTIVITY_ID, PRODUCT_ID
                    ORDER BY ACTIVITY_ID
                """
        db_data = fetch_all_from_oracle(query)
        # [
        #     ("DISP", "OIL", 16347.6),
        #     ("INVCL", "OIL", 590.4),
        #     ("INVOP", "OIL", 600.2),
        #     ("LDINJ", "OIL", 925.8),
        #     ("LDINVCL", "OIL", 114.5),
        #     ("LDINVOP", "OIL", 121.2),
        #     ("LDREC", "OIL", 932.5),
        #     ("PROD", "OIL", 15098.9),
        #     ("REC", "C5-SP", 805.6),
        #     ("REC", "OIL", 426.6),
        #     ("ROYALTY", "OIL", 2766.1),
        # ]

        data = []
        for row in db_data:
            data.append(
                {
                    "activity": row[0],
                    "product": row[1],
                    "volume": ""
                    if row[1] == "C5-SP"
                    else round(row[2], 1)
                    if unit == "metric"
                    else round(row[2], 2),
                    "adj_total": ""
                    if row[0] in ("LDINVCL", "LDINVOP", "ROYALTY")
                    else "{:.2f}".format(row[2]),
                    "notes": "SUBTRACT"
                    if row[0] in ("INVCL", "LDINJ")
                    else "IGNORE"
                    if row[0] in ("LDINVCL", "LDINVOP", "ROYALTY")
                    else ""
                    if row[0] in ("DISP",)
                    else "ADD",
                    "plot_x_name": row[0],
                    "value": row[2],
                }
            )

        for row in data:
            if row["notes"] == "SUBTRACT":
                row["value"] = -row["value"]
                row["adj_total"] = f'({row["adj_total"]})'
            if row["activity"] in ("LDINVCL", "LDINVOP", "ROYALTY"):
                row["value"] = float(0)
            if row["activity"] == "REC" and row["product"] == "OIL":
                row["plot_x_name"] = "REC-OIL"
            if row["activity"] == "REC" and row["product"] == "C5-SP":
                row["plot_x_name"] = "REC-C5"

        data.append(
            {
                "activity": "",
                "product": "",
                "volume": "",
                "adj_total": "",
                "notes": "",
                "plot_x_name": "",
                "value": float(0),
            }
        )

        data.append(data.pop(0))

        return data

    @staticmethod
    def generate_gas_table_data(pbr_battery_code, start_date, end_date, unit, rate):
        query = f"""
                    SELECT ACTIVITY_ID, 
                            PRODUCT_ID,
                            SUM(TO_NUMBER(REPLACE(VOLUME, '.', '')) / POWER(10, LENGTH(SUBSTR(VOLUME, INSTR(VOLUME, '.'))) - 1) * {rate}) AS total_volume
                    FROM PETRINEX_VOLUMETRIC_DATA
                    WHERE PRODUCT_ID IN ('GAS')
                        AND FACILITY_ID in ('{pbr_battery_code}')
                        AND ACTIVITY_ID IN ('FLARE', 'FUEL', 'PROD', 'PURREC', 'REC', 'VENT', 'DISP')
                        AND PRODUCTION_MONTH BETWEEN TO_DATE('{start_date}', 'YYYY-MM-DD') AND TO_DATE('{end_date}', 'YYYY-MM-DD')
                    GROUP BY ACTIVITY_ID, PRODUCT_ID
                    ORDER BY ACTIVITY_ID
                """
        db_data = fetch_all_from_oracle(query)

        data = []
        for row in db_data:
            data.append(
                {
                    "activity": row[0],
                    "product": row[1],
                    "volume": round(row[2], 1)
                    if unit == "metric"
                    else round(row[2], 2),
                    "adj_total": "{:.2f}".format(row[2]),
                    "notes": "SUBTRACT"
                    if row[0] in ("FLARE", "FUEL", "VENT")
                    else ""
                    if row[0] in ("DISP",)
                    else "ADD",
                    "plot_x_name": row[0],
                    "value": row[2],
                }
            )

        for row in data:
            if row["notes"] == "SUBTRACT":
                row["value"] = -row["value"]
                row["adj_total"] = f'({row["adj_total"]})'

        data.append(
            {
                "activity": "",
                "product": "",
                "volume": "",
                "adj_total": "",
                "notes": "",
                "plot_x_name": "",
                "value": float(0),
            }
        )

        data.append(data.pop(0))

        return data

    @staticmethod
    def generate_water_table_data(pbr_battery_code, start_date, end_date, unit, rate):
        query = f"""
                    SELECT ACTIVITY_ID, 
                            PRODUCT_ID,
                            SUM(TO_NUMBER(REPLACE(VOLUME, '.', '')) / POWER(10, LENGTH(SUBSTR(VOLUME, INSTR(VOLUME, '.'))) - 1) * {rate}) AS total_volume
                    FROM PETRINEX_VOLUMETRIC_DATA
                    WHERE PRODUCT_ID IN ('WATER')
                        AND FACILITY_ID in ('{pbr_battery_code}')
                        AND ACTIVITY_ID IN ('INVCL', 'INVOP', 'LDINJ', 'LDINVCL', 'LDINVOP', 'LDREC', 'PROD', 'REC', 'DISP')
                        AND PRODUCTION_MONTH BETWEEN TO_DATE('{start_date}', 'YYYY-MM-DD') AND TO_DATE('{end_date}', 'YYYY-MM-DD')
                    GROUP BY ACTIVITY_ID, PRODUCT_ID
                    ORDER BY ACTIVITY_ID
                """
        db_data = fetch_all_from_oracle(query)

        data = []
        for row in db_data:
            data.append(
                {
                    "activity": row[0],
                    "product": row[1],
                    "volume": round(row[2], 1)
                    if unit == "metric"
                    else round(row[2], 2),
                    "adj_total": ""
                    if row[0] in ("LDINVCL", "LDINVOP")
                    else "{:.2f}".format(row[2]),
                    "notes": "SUBTRACT"
                    if row[0] in ("INVCL", "LDINJ")
                    else "IGNORE"
                    if row[0] in ("LDINVCL", "LDINVOP")
                    else ""
                    if row[0] in ("DISP",)
                    else "ADD",
                    "plot_x_name": row[0],
                    "value": row[2],
                }
            )

        for row in data:
            if row["notes"] == "SUBTRACT":
                row["value"] = -row["value"]
                row["adj_total"] = f'({row["adj_total"]})'
            if row["activity"] in ("LDINVCL", "LDINVOP"):
                row["value"] = float(0)

        data.append(
            {
                "activity": "",
                "product": "",
                "volume": "",
                "adj_total": "",
                "notes": "",
                "plot_x_name": "",
                "value": float(0),
            }
        )

        data.append(data.pop(0))

        return data

    @staticmethod
    def generate_bar_plot(data, product, start_date, end_date, unit, rate):
        # Extract valid data
        activities = [row["plot_x_name"] for row in data]

        adj_totals = [row["value"] for row in data]

        # Determine colors based on adj_total values
        colors = ["red" if row["notes"] == "SUBTRACT" else "green" for row in data]
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
        ax.axhline(0, color="#E5E4E2", linewidth=0.5)

        # ===============================================
        multiple = 2000
        if unit == "imperial":
            multiple = multiple * rate

        # Set y scale with step of multiple
        max_val = max(adj_totals)
        min_val = min(adj_totals)
        ax.set_yticks(
            np.arange(
                int(PBRReportView.nearest_multiple(min_val, multiple)),
                int(PBRReportView.nearest_multiple(max_val, multiple) + multiple)
                if unit == "metric"
                else int(PBRReportView.nearest_multiple(max_val, multiple)),
                int(multiple),
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
                int(PBRReportView.nearest_multiple(max_val, multiple)),
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
                    height - 1,  # Positioning the label below the bar
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
                        height + 1,  # Slightly lower than the activity name
                        f"{adj_totals[i]:,.2f}",  # Formatting the total with commas and 2 decimal points
                        ha="center",
                        va="bottom",
                        fontsize=10,  # Font size for the adj_total values
                        color="grey",
                    )

        # Set the visibility of the x-axis label to false
        # ax.xaxis.set_visible(False)

        # Set y-axis label with LaTeX for superscript
        if product in ("oil", "water"):
            if unit == "metric":
                ax.set_ylabel(r"Total Volume (M$^3$)", fontsize=10, color="grey")
            else:
                ax.set_ylabel(r"Total Volume (BBL)", fontsize=10, color="grey")
        elif product in ("gas",):
            if unit == "metric":
                ax.set_ylabel(r"Total Volume (E$^3$M$^3$)", fontsize=10, color="grey")
            else:
                ax.set_ylabel(r"Total Volume (MCF)", fontsize=10, color="grey")

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
        plt.title(
            f"{product.upper()} BALANCE",
            color="grey",
            fontweight="bold",
            fontsize=16,
            pad=20,
        )

        plt.tight_layout()  # Adjust layout to not cut off labels

        # # Save the plot as an image file
        # image_path = os.path.join(
        #     settings.STATIC_ROOT,
        #     f'scada/images/pbr_report_{product}_bar_plot_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.png',
        # )
        # plt.savefig(f"{image_path}")
        #
        # # plt.show()
        #
        # return image_path

        # Save the plot to an in-memory buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)  # Rewind the buffer to the beginning so it can be read later

        # Return the buffer
        return buffer

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
