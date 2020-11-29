from django.shortcuts import render
from django_tables2 import SingleTableView
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView

from .forms import UserAuthenticationForm, UserRegistrationForm
from .models import User, Hour, Tool, TestedApplication
from .tables import TesterTable, TestedApplicationsTable, HoursTable, ToolsTable


def index(request):
    return render(request, template_name="automations_app/base.html")


class TestersView(SingleTableView):
    model = User
    table_class = TesterTable
    template_name = "automations_app/table.html"


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
        return super().form_valid(form)


class AuthenticateView(LoginView):
    form_class = UserAuthenticationForm
