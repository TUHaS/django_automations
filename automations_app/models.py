from django.db import models
from django.contrib.auth.models import AbstractUser


class SkillLevel(models.Model):
    name = models.CharField(max_length=100)
    salary = models.DecimalField(decimal_places=3, max_digits=9)

    def __str__(self):
        return self.name


class User(AbstractUser):
    level = models.ForeignKey(SkillLevel, on_delete=models.CASCADE,
                              related_name="level_user_fk")

    def __str__(self):
        return self.username


class TestedApplication(models.Model):
    name = models.CharField(max_length=100)
    complication = models.IntegerField()
    number_testers = models.IntegerField()


class Tool(models.Model):
    application = models.ForeignKey(TestedApplication, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    programming_language = models.CharField(max_length=100)
    open_source_code = models.CharField(max_length=100)
    complication = models.IntegerField()


class Hour(models.Model):
    number_hours = models.IntegerField()
    max_number_hours = models.IntegerField()
    application = models.ForeignKey(TestedApplication, on_delete=models.CASCADE,
                                    related_name="application_fk")
    tester = models.ForeignKey(User, on_delete=models.CASCADE)






