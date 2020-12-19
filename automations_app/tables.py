import django_tables2 as tables

from .models import User, Hour, TestedApplication, Tool


class TesterTable(tables.Table):
    username = tables.Column()
    first_name = tables.Column()
    last_name = tables.Column(verbose_name="surname")
    level = tables.Column(verbose_name="skill")
    salary = tables.Column()

    class Meta:
        model = User
        exclude = ("password", "last login", "is_superuser", "email",
                   "is_staff", "is_active", "last_login", "date_joined")


class HoursTable(tables.Table):
    tester = tables.Column(accessor="tester.id", verbose_name="tester id")
    application = tables.Column(accessor="application.id",
                                verbose_name="application id")

    class Meta:
        model = Hour


class ToolsTable(tables.Table):

    class Meta:
        model = Tool


class TestedApplicationsTable(tables.Table):
    class Meta:
        model = TestedApplication