from django.db import models


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("ФИО", max_length=255)
    group_number = models.CharField("Группа", max_length=100)
    record_book = models.CharField("Зачётная книжка", max_length=100,
                                   blank=True)

    class Meta:
        db_table = "students"
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"

    def __str__(self):
        return self.name
