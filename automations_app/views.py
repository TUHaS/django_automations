import io
from datetime import timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from django.utils import timezone
from django.shortcuts import render
from django.http import JsonResponse
from django_tables2 import SingleTableView
from django.core.files.storage import default_storage
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.db.models import Q
from rest_framework import permissions
from rest_framework.generics import views

from .forms import UserAuthenticationForm, UserRegistrationForm
from .models import User, Hour, Tool, TestedApplication
from .tables import TesterTable, TestedApplicationsTable, HoursTable, ToolsTable


# контроллер в виде функции, который только рендерит html-страницу
def index(request):
    return render(request, template_name="automations_app/base.html")


class TestersView(SingleTableView, views.APIView):
    model = User
    table_class = TesterTable
    paginate_by = 10  # кол-во записей на страницу таблицы
    template_name = "automations_app/table_user.html"
    permission_classes = [permissions.IsAdminUser]

    # описание логики веб-приложения при поступлении POST запроса на
    # URL-адрес, к которому привязан этот класс
    def post(self, request):
        response_context = {}

        datetime_now = timezone.now()
        datetime_year = datetime_now - timedelta(days=365*2)

        # выборка данных за последние 2 года по проектам, которые завершились
        objs_hours = Hour.objects.filter(
            ~Q(application__end_project=None)
            & Q(application__start_project__range=(datetime_year, datetime_now))
        )
        users_info = dict()
        #
        if len(objs_hours) > 0:
            # заполнение словаря с необработанными данными
            for idx, obj in enumerate(objs_hours):
                user_id = obj.tester.id
                proj_hour = obj.number_hours
                if user_id not in users_info:
                    salary = obj.tester.salary
                    users_info[user_id] = {
                        "salary": float(salary),
                        "finished_projects": 1,
                        "hours": [proj_hour]
                    }
                else:
                    users_info[user_id]["finished_projects"] += 1
                    users_info[user_id]["hours"].append(proj_hour)

            # подготовка numpy-массива, который будет использоваться в KMeans
            array = np.zeros((len(users_info), 4), dtype=np.uint)
            for idx, user_id in enumerate(users_info):
                user_data = users_info[user_id]
                avg_hours = np.average(user_data["hours"])
                array[idx, 0] = avg_hours
                array[idx, 1] = user_data["finished_projects"]
                array[idx, 2] = user_data["salary"]
                array[idx, 3] = user_id
            only_data = array[:, :3]
            # нормализация данных
            mms = MinMaxScaler()
            mms.fit(only_data)
            data_mms = mms.transform(only_data)
            # вычисление центров для масс и получение меток для выборки
            labels = KMeans(n_clusters=3, random_state=0).fit_predict(data_mms)
            # преобразование результата в бинарный формат
            if request.data['type'] == 'image':
                file = self.get_image_bytes(only_data, labels)
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
        # визуализация данных
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(array[:, 0], array[:, 1], array[:, 2], c=labels,
                   cmap='viridis', edgecolors='k')
        ax.set_title("Clustering result")
        ax.set_xlabel("avg hours")
        ax.set_ylabel("num finish projects")
        ax.set_zlabel("salary of user")
        ax.dist = 10
        fig.savefig(pic_bytes, format="png")
        pic_bytes.seek(0)
        return pic_bytes

    @staticmethod
    def get_excel_bytes(array, labels):
        array_copy = array.copy()
        new_data = np.zeros((array_copy.shape[0], array_copy.shape[1]+1),
                            dtype=np.float)
        # объединение данных из БД с метками из результата KMeans
        new_data[:, 0] = array[:, 3]
        new_data[:, 1] = array[:, 0]
        new_data[:, 2] = array[:, 1]
        new_data[:, 3] = array[:, 2]
        new_data[:, 4] = labels
        data_bytes = io.BytesIO()
        df = pd.DataFrame(new_data, columns=["Tester ID", "Average Hours",
                                             "Finish projects number", "Salary",
                                             "KMeans Group ID"])
        # сохранение данных в excel формате в объект BytesIO
        df.to_excel(data_bytes, index=False, encoding='utf-8')
        data_bytes.seek(0)
        return data_bytes


# наследование от класса SingleTableView позволяет не описывать то,
# как нужно извлекать данные из БД и выводить таблицу в html-страницу в ответ
# на GET запрос пользователя - эти действия происходят в подключенном стороннем
# приложении django-tables2
class TestedApplicationsView(SingleTableView, views.APIView):
    model = TestedApplication
    table_class = TestedApplicationsTable
    template_name = "automations_app/table.html"
    permission_classes = [permissions.IsAuthenticated]
    paginate_by = 10


class ToolsView(SingleTableView, views.APIView):
    # определение модели (таблицы), из которой извлекаются записи
    model = Tool
    # определение класса для описывания внешнего вида таблицы на веб-странице
    table_class = ToolsTable
    # определение пути к html-шаблону, который будет рендериться
    template_name = "automations_app/table.html"
    permission_classes = [permissions.IsAuthenticated]
    paginate_by = 10


class HoursView(SingleTableView, views.APIView):
    model = Hour
    table_class = HoursTable
    template_name = "automations_app/table.html"
    # не аутентифицированные пользователи не смогут просмотреть страницу
    # (вернёт ошибку 403 Forbidden)
    permission_classes = [permissions.IsAuthenticated]
    paginate_by = 10


# класс-контроллер отвечает за логику веб-приложения при взаимодействии
# с формой регистрации
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
