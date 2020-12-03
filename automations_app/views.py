import io
import base64

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from django.shortcuts import render
from django_tables2 import SingleTableView
from django_tables2 import RequestConfig
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
    template_name = "automations_app/table_user.html"
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        # получение всех записей из модели (таблицы) Hour
        objs_hours = Hour.objects.all()
        array = np.zeros((len(objs_hours), 2), dtype=np.float)
        # формирование выборки (сложность проекта + зарплата тестера)
        for idx, obj in enumerate(objs_hours):
            array[idx, 0] = obj.application.complication
            array[idx, 1] = float(obj.tester.salary)
        # вычисление центров для масс и получение меток для выборки
        labels = KMeans(n_clusters=3, random_state=0).fit_predict(array)
        # преобразование изображения в base64
        img = self.plot_to_base64(array, labels)
        # формирование объекта таблицы (django-tables2)
        table = self.table_class(User.objects.all())
        # настройка пагинатора таблицы (ограничение в 10 записей на страницу)
        RequestConfig(request, paginate={"per_page": 10}).configure(table)
        context = {"image": img, 'table': table}
        # возвращение ответа на запрос (рендеринг HTML шаблона и передача в него изображения
        return render(request, self.template_name, context)

    @staticmethod
    def plot_to_base64(array, labels):
        pic_bytes = io.BytesIO()
        plt.scatter(array[:, 0], array[:, 1], c=labels)
        plt.savefig(pic_bytes, format="png")
        pic_bytes.seek(0)
        image_data = base64.b64encode(pic_bytes.read()).decode('utf-8')
        return image_data


class TestedApplicationsView(SingleTableView, views.APIView):
    model = TestedApplication
    table_class = TestedApplicationsTable
    template_name = "automations_app/table.html"
    permission_classes = [permissions.IsAuthenticated]


class ToolsView(SingleTableView, views.APIView):
    model = Tool
    table_class = ToolsTable
    template_name = "automations_app/table.html"
    permission_classes = [permissions.IsAuthenticated]


class HoursView(SingleTableView, views.APIView):
    model = Hour
    table_class = HoursTable
    template_name = "automations_app/table.html"
    permission_classes = [permissions.IsAuthenticated]


class RegistrationView(FormView):
    form_class = UserRegistrationForm
    template_name = "registration/register.html"
    success_url = "/"

    def form_valid(self, form):
        form.save()
        username = self.request.POST['username']
        password = self.request.POST['password1']
        # заходим под пользователем после регистрации,
        # чтобы он не проходил аутентификацию снова
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return super().form_valid(form)


class AuthenticateView(LoginView):
    form_class = UserAuthenticationForm
