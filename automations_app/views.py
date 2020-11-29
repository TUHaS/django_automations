from django.shortcuts import render
from django_tables2 import SingleTableView
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login
from rest_framework import permissions
from rest_framework.generics import views

from .forms import UserAuthenticationForm, UserRegistrationForm
from .models import User, Hour, Tool, TestedApplication
from .tables import TesterTable, TestedApplicationsTable, HoursTable, ToolsTable


def index(request):
    return render(request, template_name="automations_app/base.html")


class TestersView(SingleTableView, views.APIView):
    model = User
    table_class = TesterTable
    template_name = "automations_app/table.html"
    permission_classes = [permissions.IsAdminUser]


class TestedApplicationsView(SingleTableView):
    model = TestedApplication
    table_class = TestedApplicationsTable
    template_name = "automations_app/table.html"


class ToolsView(SingleTableView):
    model = Tool
    table_class = ToolsTable
    template_name = "automations_app/table.html"


class HoursView(SingleTableView):
    model = Hour
    table_class = HoursTable
    template_name = "automations_app/table.html"


class RegistrationView(FormView):
    form_class = UserRegistrationForm
    template_name = "registration/register.html"
    success_url = "/"

    def form_valid(self, form):
        form.save()
        username = self.request.POST['username']
        password = self.request.POST['password1']
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return super().form_valid(form)


class AuthenticateView(LoginView):
    form_class = UserAuthenticationForm
