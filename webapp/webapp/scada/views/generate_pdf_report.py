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
    "logo_url": os.path.join(
        settings.STATIC_ROOT, "scada/images/ico/apple-touch-icon-144.png"
    ),
}


class ReportView(View):
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

        data = ReportView.generate_fake_data(start_date, end_date)
        scatter_plot_image_path = ReportView.generate_scatter_plot(data, month, year)
        line_plot_image_path = ReportView.generate_line_plot(data, month, year)
        bar_plot_image_path = ReportView.generate_bar_plot(data, month, year)

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
