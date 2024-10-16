from django.urls import path
from .views import (
    home,
    contact,
    subscribe,
    sign_in,
    sign_up,
    sign_out,
    generate_pdf_report,
    generate_pbr_report,
    reset_password,
    ai,
    profile,
    search_facility_ids,
)

app_name = "scada"

urlpatterns = [
    path("home/", home.HomeView.as_view(), name="home"),
    path("contact/", contact.ContactView.as_view(), name="contact"),
    path("subscribe/", subscribe.SubscribeView.as_view(), name="subscribe"),
    path("dashboard/", sign_in.SignInView.as_view(), name="dashboard"),
    path("sign-up/", sign_up.SignUpView.as_view(), name="sign-up"),
    path("sign-out/", sign_out.SignOutView.as_view(), name="sign-out"),
    path(
        "reset-password/",
        reset_password.ResetPasswordView.as_view(),
        name="reset-password",
    ),
    path(
        "pdf-report-1/",
        generate_pdf_report.MonthlyReportView.as_view(),
        name="pdf-report-1",
    ),
    path(
        "pdf-report-2/",
        generate_pdf_report.GeneralReportView.as_view(),
        name="pdf-report-2",
    ),
    path(
        "pdf-pbr-report/",
        generate_pbr_report.PBRReportView.as_view(),
        name="pdf-pbr-report",
    ),
    path("ai/", ai.AiView.as_view(), name="ai"),
    path("profile/<int:user_id>/", profile.ProfileView.as_view(), name="profile"),
    path(
        "search-facility-ids/",
        search_facility_ids.SearchFacilityIdsView.as_view(),
        name="search_facility_ids",
    ),
]
