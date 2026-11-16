from django.db import models


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    group_number = models.CharField(max_length=100)
    record_book = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "students"

    def __str__(self):
        return self.name
