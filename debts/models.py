from django.db import models


class DebtQuerySet(models.QuerySet):
    def open(self):
        return self.filter(is_closed=False)

    def closed(self):
        return self.filter(is_closed=True)


class Debt(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="debts",
        verbose_name="Студент",
    )
    discipline = models.ForeignKey(
        "homepage.Discipline", on_delete=models.CASCADE,
        related_name="debts", verbose_name="Дисциплина",
    )
    date_created = models.DateField("Дата задолженности")
    is_closed = models.BooleanField("Закрыта", default=False)

    objects = DebtQuerySet.as_manager()

    class Meta:
        db_table = "debts"
        verbose_name = "Задолженность"
        verbose_name_plural = "Задолженности"

    def __str__(self):
        return f"Задолженность №{self.pk}: {self.student} — {self.discipline}"
