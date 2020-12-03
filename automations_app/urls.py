from django.urls import re_path, include, path

from . import views

app_name = "automations_app"
urlpatterns = [
    path("", views.index, name="home"),
    re_path("^testers/?$", views.TestersView.as_view(), name="testers"),
    re_path("^hours/?$", views.HoursView.as_view(), name="hours"),
    re_path("^tools/?$", views.ToolsView.as_view(), name="tools"),
    re_path("^tested-apps/?$", views.TestedApplicationsView.as_view(),
            name="tested-apps"),
    path('', include("django.contrib.auth.urls")),
    re_path("^login/?$", views.AuthenticateView.as_view(), name="login"),
    re_path("^register/?$", views.RegistrationView.as_view(), name="register"),
]
