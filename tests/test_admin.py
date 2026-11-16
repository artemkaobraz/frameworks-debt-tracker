import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connections
from django.test import Client
from django.test.utils import CaptureQueriesContext

from db.database import PROJECT_ROOT, get_connection
from db.import_json import import_data
from debts.models import Debt
from homepage.models import Discipline
from students.models import Student


@pytest.fixture
def migrated_database(tmp_path):
    database_path = tmp_path / "admin_test.sqlite"
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
        yield connection
    finally:
        connection.close()
        connection.settings_dict["NAME"] = original_path


def test_models_are_registered_and_admin_pages_work(migrated_database):
    for model in (Student, Discipline, Debt):
        assert model in admin.site._registry
    assert Student._meta.verbose_name == "Студент"
    assert Discipline._meta.verbose_name_plural == "Дисциплины"
    assert Debt._meta.get_field("is_closed").verbose_name == "Закрыта"

    user = get_user_model().objects.create(
        username="admin-test", is_staff=True, is_superuser=True
    )
    client = Client()
    client.force_login(user)
    for url in (
        "/admin/", "/admin/students/student/",
        "/admin/homepage/discipline/", "/admin/debts/debt/",
    ):
        assert client.get(url).status_code == 200

    student_page = client.get("/admin/students/student/1/change/")
    assert student_page.status_code == 200
    assert "Задолженности" in student_page.content.decode()
    discipline_page = client.get("/admin/homepage/discipline/1/change/")
    assert discipline_page.status_code == 200
    assert "Задолженности" in discipline_page.content.decode()
    debt_page = client.get("/admin/debts/debt/1/change/")
    assert debt_page.status_code == 200
    assert "Дата задолженности" in debt_page.content.decode()


def test_debt_filters_stats_and_related_queries(migrated_database):
    student = Student.objects.create(name="Тестовый студент",
                                     group_number="Т-1", record_book="T1")
    discipline = Discipline.objects.create(name="Тестовая дисциплина",
                                           teacher="Тест", semester=1)
    Debt.objects.create(student=student, discipline=discipline,
                        date_created="2026-01-10", is_closed=False)
    Debt.objects.create(student=student, discipline=discipline,
                        date_created="2026-02-10", is_closed=True)
    assert Debt.objects.open().filter(student=student).count() == 1
    assert Debt.objects.closed().filter(student=student).count() == 1

    client = Client()
    filters = (
        f"student_id={student.pk}&discipline_id={discipline.pk}"
        "&date_from=2026-01-01&date_to=2026-01-31"
        "&status=open&sort=discipline"
    )
    filtered = client.get(f"/debts/?{filters}")
    content = filtered.content.decode()
    assert filtered.status_code == 200
    assert "Всего задолженностей: 1" in content
    assert "Тестовый студент" in content
    assert "Тестовая дисциплина" in content
    assert "2026-01-01" in content
    assert "2026-01-31" in content
    assert "Всего задолженностей: 0" in client.get(
        f"/debts/?student_id={student.pk}&status=closed"
        "&date_to=2026-01-31"
    ).content.decode()

    stats = client.get("/debts/statistics/").content.decode()
    assert f"Всего активных задолженностей: {Debt.objects.open().count()}" \
        in stats
    assert "Тестовый студент. Активных задолженностей: 1" in stats

    Debt.objects.bulk_create([
        Debt(student=student, discipline=discipline,
             date_created="2026-01-10", is_closed=False)
        for _ in range(12)
    ])
    with CaptureQueriesContext(migrated_database) as queries:
        page = client.get(
            f"/debts/?student_id={student.pk}&status=open"
            "&sort=discipline&page=2"
        )
        page_content = page.content.decode()
    assert page.status_code == 200
    assert "Страница 2" in page_content
    assert f"student_id={student.pk}" in page_content
    assert "status=open" in page_content
    assert "sort=discipline" in page_content
    assert len(queries) <= 4
