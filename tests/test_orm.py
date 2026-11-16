from django.core.management import call_command
from django.db import connections
from django.test import Client

from db.database import PROJECT_ROOT, get_connection
from db.import_json import import_data
from debts.models import Debt
from homepage.models import Discipline
from students.models import Student


def test_existing_database_migrates_and_supports_orm_workflows(tmp_path):
    database_path = tmp_path / "debt_track.sqlite"
    source_connection = get_connection(database_path)
    try:
        import_data(source_connection, PROJECT_ROOT / "data")
        tables = {
            row[0]
            for row in source_connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        assert tables == {"students", "disciplines", "debts"}
    finally:
        source_connection.close()
    connection = connections["default"]
    original_path = connection.settings_dict["NAME"]
    connection.close()
    connection.settings_dict["NAME"] = database_path
    try:
        call_command("migrate", fake_initial=True, interactive=False,
                     verbosity=0)
        assert Student.objects.count() == 3
        assert Discipline.objects.count() == 2
        assert Debt.objects.count() == 3
        assert Debt.objects.select_related("student", "discipline").get(
            pk=1
        ).student.name == "Анна Смирнова"

        client = Client()
        assert "Анна Смирнова" in client.get(
            "/students/?q=Анна&sort=debt_count"
        ).content.decode()
        assert "Анна Смирнова" in client.get(
            "/debts/?status=open&q=Анна"
        ).content.decode()
        assert "Мария Волкова" in client.get(
            "/students/clean/"
        ).content.decode()

        response = client.post("/students/new/", {
            "name": "Тестовый студент", "group_number": "Т-1",
            "record_book": "123",
        })
        assert response.status_code == 302
        student = Student.objects.get(name="Тестовый студент")
        response = client.post(f"/students/{student.pk}/edit/", {
            "name": "Обновлённый студент", "group_number": "Т-2",
            "record_book": "123",
        })
        assert response.status_code == 302
        student.refresh_from_db()
        assert student.name == "Обновлённый студент"

        response = client.post("/disciplines/new/", {
            "name": "Тестовая дисциплина", "teacher": "Преподаватель",
            "semester": 1,
        })
        assert response.status_code == 302
        discipline = Discipline.objects.get(name="Тестовая дисциплина")
        response = client.post("/debts/new/", {
            "student": student.pk, "discipline": discipline.pk,
            "date_created": "2026-11-16", "is_closed": "on",
        })
        assert response.status_code == 302
        debt = Debt.objects.get(student=student, discipline=discipline)
        assert debt.is_closed
        assert client.post(f"/debts/{debt.pk}/delete/").status_code == 302
        assert not Debt.objects.filter(pk=debt.pk).exists()
        assert client.post(
            f"/disciplines/{discipline.pk}/delete/"
        ).status_code == 302
        assert client.post(
            f"/students/{student.pk}/delete/"
        ).status_code == 302

        Debt.objects.bulk_create([
            Debt(student_id=1, discipline_id=1,
                 date_created="2026-11-16")
            for _ in range(12)
        ])
        page = client.get("/debts/?status=open&sort=student&page=2")
        assert page.status_code == 200
        assert "Страница 2" in page.content.decode()
        assert "status=open" in page.content.decode()
        assert "sort=student" in page.content.decode()
    finally:
        connection.close()
        connection.settings_dict["NAME"] = original_path
