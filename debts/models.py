from django.db import models


class Debt(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="debts"
    )
    discipline = models.ForeignKey(
        "homepage.Discipline", on_delete=models.CASCADE,
        related_name="debts",
    )
    date_created = models.DateField()
    is_closed = models.BooleanField(default=False)

    class Meta:
        db_table = "debts"

    def __str__(self):
        return f"{self.student}: {self.discipline}"
