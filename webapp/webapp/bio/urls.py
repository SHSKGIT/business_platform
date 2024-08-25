from django.urls import path
from .views import home

app_name = 'bio'

urlpatterns = [
    path("home/", home.HomeView.as_view(), name="home"),
]