from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    LEVEL_CHOICES = [
        ("Junior", "Junior"),
        ("Senior", "Senior"),
        ("Middle", "Middle")
    ] # ограничиваем выбор значений поля только этими вариантами
    level = models.CharField(max_length=6, choices=LEVEL_CHOICES,
                             default="Junior")
    salary = models.DecimalField(decimal_places=0, max_digits=9, default=0.00)

    # для вывода логина пользователя в админ-панели в качестве ссылки на запись
    # в БД вместо стандартного Object(1), Object(2) и т.д.
    def __str__(self):
        return self.username

    class Meta:
        # название таблицы в админ-панели (по умолчанию берётся название класса)
        verbose_name = "Tester"
        # название таблицы в админ-панели во множественном числе
        verbose_name_plural = "Testers"


class TestedApplication(models.Model):
    # CharField соответствует VARCHAR в БД
    name = models.CharField(max_length=100)
    # если в скобках не указан параметр null=True, значит поле ненулевое
    complication = models.IntegerField()
    # если в скобках не указан параметр default=значение, значит значения
    # по умолчанию оно не имеет
    number_testers = models.IntegerField()
    # DecimalField соответствует домену DECIMAL в MySQL
    # параметр decimal_places задает кол-во знаков после запятой,
    # а max_digits - максимальное кол-во цифр
    coverage_percent = models.DecimalField(decimal_places=2, max_digits=5,
                                           default=0.00)

    start_project = models.DateTimeField(null=True, default=timezone.now)
    end_project = models.DateTimeField(null=True, blank=True)

    # ForeignKey задаёт связь many-to-one с другой таблицей
    # (с какой именно - указывается первым параметром)
    tool = models.ForeignKey('Tool', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class Tool(models.Model):
    name = models.CharField(max_length=100)
    programming_language = models.CharField(max_length=100)
    open_source_code = models.CharField(max_length=100)
    complication = models.IntegerField()

    def __str__(self):
        return self.name


class Hour(models.Model):
    number_hours = models.IntegerField()
    max_number_hours = models.IntegerField()
    application = models.ForeignKey(TestedApplication, on_delete=models.CASCADE,
                                    related_name="application_fk")
    tester = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.application.name





