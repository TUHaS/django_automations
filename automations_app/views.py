import io
import base64

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from django.shortcuts import render
from django.http import JsonResponse
from django_tables2 import SingleTableView
from django.core.files.storage import default_storage
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login
from django.conf import settings
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
    paginate_by = 10  # кол-во записей на страницу таблицы
    template_name = "automations_app/table_user.html"
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        response_context = {}
        # получение всех записей из модели (таблицы) Hour
        objs_hours = Hour.objects.all()
        array = np.zeros((len(objs_hours), 2), dtype=np.float)
        if len(objs_hours) > 0:
            # формирование выборки (сложность проекта + зарплата тестера)
            for idx, obj in enumerate(objs_hours):
                array[idx, 0] = obj.application.complication
                array[idx, 1] = float(obj.tester.salary)
            # вычисление центров для масс и получение меток для выборки
            labels = KMeans(n_clusters=3, random_state=0).fit_predict(array)
            # преобразование результата в бинарный формат
            if request.data['type'] == 'image':
                file = self.get_image_bytes(array, labels)
                filename = 'image.jpeg'
            elif request.data['type'] == 'clustering-data':
                file = self.get_excel_bytes(array, labels)
                filename = 'data.xlsx'
            else:
                return JsonResponse(response_context, status=400)
            # сохранение файла на сервере
            res_filename = default_storage.save(filename, file)
            target_url = request.build_absolute_uri(settings.MEDIA_URL + res_filename)
            response_context["path"] = target_url
        # возвращение ответа клиенту
        return JsonResponse(response_context, status=200)

    @staticmethod
    def get_image_bytes(array, labels):
        pic_bytes = io.BytesIO()
        plt.scatter(array[:, 0], array[:, 1], c=labels)
        plt.savefig(pic_bytes, format="png")
        pic_bytes.seek(0)
        return pic_bytes

    @staticmethod
    def get_excel_bytes(array, labels):
        array_copy = array.copy()
        new_data = np.zeros((array_copy.shape[0], array_copy.shape[1]+1),
                            dtype=np.float)
        new_data[:, 0] = array[:, 0]
        new_data[:, 1] = array[:, 1]
        new_data[:, 2] = labels
        data_bytes = io.BytesIO()
        df = pd.DataFrame(new_data, columns=["Complication", "Salary",
                                             "KMeans Group ID"])
        df.to_excel(data_bytes, index=False, encoding='utf-8')
        data_bytes.seek(0)
        return data_bytes


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
