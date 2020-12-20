import django_tables2 as tables

from .models import User, Hour, TestedApplication, Tool


# классы описывают колонки, которые будут выводиться в таблице и выбираться из БД, если они там есть;
# порядок задания колонок определяет очередность их отображения на веб-странице
class TesterTable(tables.Table):
    username = tables.Column()
    first_name = tables.Column()
    # verbose_name задает отображаемое название столбца на веб-странице,
    # если не задать - будет отображаться имя этой переменной
    last_name = tables.Column(verbose_name="surname")
    level = tables.Column(verbose_name="skill")
    salary = tables.Column()

    class Meta:
        # определяем модель (таблицу в БД), из которой извлекаются записи
        model = User
        # в exclude указываются название колонок,
        # которые не нужно выводить на веб-странице (по умолчанию выводятся все)
        exclude = ("password", "last login", "is_superuser", "email",
                   "is_staff", "is_active", "last_login", "date_joined")


class HoursTable(tables.Table):
    # accessor позволяет получить доступ
    # к данным из другой модели через внешний ключ
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
