from django.db import models


class Discipline(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("Название", max_length=255)
    teacher = models.CharField("Преподаватель", max_length=255, blank=True)
    semester = models.IntegerField("Семестр")

    class Meta:
        db_table = "disciplines"
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"

    def __str__(self):
        return self.name
