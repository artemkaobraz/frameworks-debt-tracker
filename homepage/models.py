from django.db import models


class Discipline(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    teacher = models.CharField(max_length=255, blank=True)
    semester = models.IntegerField()

    class Meta:
        db_table = "disciplines"

    def __str__(self):
        return self.name
