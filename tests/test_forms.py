from datetime import timedelta

import pytest
from django.core.management import call_command
from django.db import connections
from django.test import Client
from django.utils import timezone

from db.database import PROJECT_ROOT, get_connection
from db.import_json import import_data
from debts.forms import DebtFilterForm, DebtForm
from debts.models import Debt
from homepage.models import Discipline
from students.models import Student


@pytest.fixture
def migrated_database(tmp_path):
    database_path = tmp_path / "forms_test.sqlite"
    source_connection = get_connection(database_path)
    try:
        import_data(source_connection, PROJECT_ROOT / "data")
    finally:
        source_connection.close()
    connection = connections["default"]
    original_path = connection.settings_dict["NAME"]
    connection.close()
    connection.settings_dict["NAME"] = database_path
    try:
        call_command("migrate", fake_initial=True, interactive=False,
                     verbosity=0)
        yield
    finally:
        connection.close()
        connection.settings_dict["NAME"] = original_path


def test_filter_form_validates_and_preserves_pagination(migrated_database):
    assert DebtFilterForm({"status": "open"}).is_valid()
    assert not DebtFilterForm({"student_id": "abc"}).is_valid()
    assert not DebtFilterForm({"date_from": "2026-02-01",
                               "date_to": "2026-01-01"}).is_valid()
    client = Client()
    invalid = client.get("/debts/?student_id=abc")
    assert invalid.status_code == 200
    assert "Введите целое число" in invalid.content.decode()
    assert "Всего задолженностей: 3" in invalid.content.decode()

    student = Student.objects.create(name="Тестовый студент",
                                     group_number="Т-1", record_book="T1")
    discipline = Discipline.objects.create(name="Тестовая дисциплина",
                                           teacher="Тест", semester=1)
    Debt.objects.bulk_create([
        Debt(student=student, discipline=discipline,
             date_created=timezone.localdate(), is_closed=False)
        for _ in range(12)
    ])
    response = client.get(
        f"/debts/?student_id={student.pk}&status=open&sort=student&page=2"
    )
    content = response.content.decode()
    assert response.status_code == 200
    assert "Страница 2" in content
    assert f"student_id={student.pk}" in content
    assert "status=open" in content
    assert "sort=student" in content


def test_debt_form_create_edit_duplicate_and_future_date(migrated_database):
    student = Student.objects.create(name="Новый студент",
                                     group_number="Т-2", record_book="T2")
    discipline = Discipline.objects.create(name="Новая дисциплина",
                                           teacher="Тест", semester=2)
    client = Client()
    payload = {
        "student": student.pk,
        "discipline": discipline.pk,
        "date_created": timezone.localdate().isoformat(),
    }
    assert DebtForm(payload).is_valid()
    assert client.post("/debts/new/", payload).status_code == 302
    debt = Debt.objects.get(student=student, discipline=discipline)
    edit_page = client.get(
        f"/debts/{debt.pk}/edit/"
    ).content.decode()
    assert "type=\"date\"" in edit_page
    assert f'value="{timezone.localdate().isoformat()}"' in edit_page

    duplicate = client.post("/debts/new/", payload)
    assert duplicate.status_code == 200
    assert "уже есть активная задолженность" in duplicate.content.decode()
    assert Debt.objects.filter(student=student,
                               discipline=discipline).count() == 1
    assert client.post(f"/debts/{debt.pk}/edit/", payload).status_code == 302

    future_payload = {**payload, "date_created": (
        timezone.localdate() + timedelta(days=1)
    ).isoformat()}
    future = client.post("/debts/new/", future_payload)
    assert future.status_code == 200
    assert "не может быть в будущем" in future.content.decode()
    incomplete = client.post("/debts/new/", {"date_created": payload[
        "date_created"
    ]})
    assert incomplete.status_code == 200
    assert "Обязательное поле" in incomplete.content.decode()

    closed_payload = {**payload, "is_closed": "on"}
    assert client.post("/debts/new/", closed_payload).status_code == 302
    assert Debt.objects.closed().filter(student=student,
                                        discipline=discipline).count() == 1
    closed_debt = Debt.objects.closed().get(student=student,
                                            discipline=discipline)
    conflicting_edit = client.post(
        f"/debts/{closed_debt.pk}/edit/", payload
    )
    assert conflicting_edit.status_code == 200
    assert "уже есть активная задолженность" in \
        conflicting_edit.content.decode()
    closed_debt.refresh_from_db()
    assert closed_debt.is_closed


def test_close_action_requires_post_and_csrf(migrated_database):
    student = Student.objects.create(name="Студент для закрытия",
                                     group_number="Т-3", record_book="T3")
    discipline = Discipline.objects.create(name="Предмет для закрытия",
                                           teacher="Тест", semester=3)
    debt = Debt.objects.create(student=student, discipline=discipline,
                               date_created=timezone.localdate(),
                               is_closed=False)
    client = Client(enforce_csrf_checks=True)
    close_url = f"/debts/{debt.pk}/close/"
    assert client.get(close_url).status_code == 405
    assert client.post(close_url).status_code == 403
    detail = client.get(f"/debts/{debt.pk}/")
    assert "Закрыть задолженность" in detail.content.decode()
    csrf_token = client.cookies["csrftoken"].value
    closed = client.post(close_url, {"csrfmiddlewaretoken": csrf_token})
    assert closed.status_code == 302
    debt.refresh_from_db()
    assert debt.is_closed
    assert "Закрыть задолженность" not in client.get(
        f"/debts/{debt.pk}/"
    ).content.decode()
    assert client.post("/debts/9999/close/", {
        "csrfmiddlewaretoken": csrf_token,
    }).status_code == 404
    assert Client().post("/debts/new/", {
        "student": student.pk, "discipline": discipline.pk,
        "date_created": timezone.localdate().isoformat(),
    }).status_code == 302
