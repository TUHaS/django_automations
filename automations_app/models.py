from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


# class SkillLevel(models.Model):
#     name = models.CharField(max_length=100)
#     salary = models.DecimalField(decimal_places=0, max_digits=9)
#
#     def __str__(self):е
#         return self.name


class User(AbstractUser):
    # level = models.ForeignKey(SkillLevel, on_delete=models.CASCADE,
    #                           related_name="level_user_fk", null=True)
    LEVEL_CHOICES = [
        ("Junior", "Junior"),
        ("Senior", "Senior"),
        ("Middle", "Middle")
    ]
    level = models.CharField(max_length=6, choices=LEVEL_CHOICES,
                             default="Junior")
    salary = models.DecimalField(decimal_places=0, max_digits=9, default=0.00)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Tester"
        verbose_name_plural = "Testers"


class TestedApplication(models.Model):
    name = models.CharField(max_length=100)
    complication = models.IntegerField()
    number_testers = models.IntegerField()
    coverage_percent = models.DecimalField(decimal_places=2, max_digits=5,
                                           default=0.00)
    start_project = models.DateTimeField(null=True, default=timezone.now)
    end_project = models.DateTimeField(null=True, blank=True)
    # is_finish = models.BooleanField(default=False)
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





