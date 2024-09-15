from django.urls import path
from .views import (
    home,
    contact,
    subscribe,
    sign_in,
    sign_up,
    sign_out,
    generate_pdf_report,
    reset_password,
    ai,
)

app_name = "scada"

urlpatterns = [
    path("home/", home.HomeView.as_view(), name="home"),
    path("contact/", contact.ContactView.as_view(), name="contact"),
    path("subscribe/", subscribe.SubscribeView.as_view(), name="subscribe"),
    path("sign-in/", sign_in.SignInView.as_view(), name="sign-in"),
    path("sign-up/", sign_up.SignUpView.as_view(), name="sign-up"),
    path("sign-out/", sign_out.SignOutView.as_view(), name="sign-out"),
    path(
        "reset-password/",
        reset_password.ResetPasswordView.as_view(),
        name="reset-password",
    ),
    path(
        "pdf-report-1/", generate_pdf_report.ReportView.as_view(), name="pdf-report-1"
    ),
    path("ai/", ai.AiView.as_view(), name="ai"),
]
