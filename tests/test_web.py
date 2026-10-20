import sqlite3
from unittest.mock import patch

from django.template.loader import get_template
from django.test import Client
from django.test import override_settings


def test_templates_are_available_in_expected_locations() -> None:
    template_names = [
        "base.html",
        "includes/navigation.html",
        "homepage/index.html",
        "students/student_list.html",
        "students/student_detail.html",
        "students/clean_students.html",
        "students/includes/student_card.html",
        "debts/debt_list.html",
        "debts/debt_detail.html",
        "debts/statistics.html",
        "debts/includes/debt_status.html",
    ]

    for template_name in template_names:
        assert get_template(template_name) is not None


def test_homepage_uses_base_navigation_and_static_files() -> None:
    response = Client().get("/")
    content = response.content.decode()

    assert response.status_code == 200
    assert "/static/homepage/css/style.css" in content
    assert "/static/homepage/js/main.js" in content
    assert '<h1 class="site-brand">' in content
    assert "/disciplines/" in content


def test_list_pages_use_app_templates_and_includes() -> None:
    client = Client()
    students_response = client.get("/students/")
    debts_response = client.get("/debts/")

    assert "Всего студентов:" in students_response.content.decode()
    assert "Подробнее" in students_response.content.decode()
    assert "Всего задолженностей:" in debts_response.content.decode()
    assert "активна" in debts_response.content.decode()


def test_list_pages_show_loaded_data() -> None:
    client = Client()
    students_response = client.get("/students/")
    debts_response = client.get("/debts/")
    disciplines_response = client.get("/disciplines/")

    assert students_response.status_code == 200
    assert "Анна Смирнова" in students_response.content.decode()
    assert debts_response.status_code == 200
    assert "Математический анализ" in debts_response.content.decode()
    assert disciplines_response.status_code == 200
    assert "Информатика" in disciplines_response.content.decode()


def test_detail_pages_show_loaded_data() -> None:
    client = Client()
    student_response = client.get("/students/1/")
    debt_response = client.get("/debts/1/")

    assert student_response.status_code == 200
    assert "ЭФБО-02-24" in student_response.content.decode()
    assert debt_response.status_code == 200
    assert "Анна Смирнова" in debt_response.content.decode()


def test_missing_objects_return_404_with_detail_templates() -> None:
    client = Client()
    student_response = client.get("/students/999/")
    debt_response = client.get("/debts/999/")

    assert student_response.status_code == 404
    assert "Студент не найден" in student_response.content.decode()
    assert debt_response.status_code == 404
    assert "Задолженность не найдена" in debt_response.content.decode()


def test_empty_collections_have_messages() -> None:
    def empty_connection():
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        connection.executescript(
            """
            CREATE TABLE students (
                id INTEGER PRIMARY KEY, name TEXT, group_number TEXT,
                record_book TEXT
            );
            CREATE TABLE disciplines (
                id INTEGER PRIMARY KEY, name TEXT, teacher TEXT,
                semester INTEGER
            );
            CREATE TABLE debts (
                id INTEGER PRIMARY KEY, student_id INTEGER,
                discipline_id INTEGER, date_created TEXT,
                is_closed INTEGER
            );
            """
        )
        return connection

    with patch("students.views.get_connection", empty_connection):
        students_response = Client().get("/students/")
    with patch("debts.views.get_connection", empty_connection):
        debts_response = Client().get("/debts/")

    assert "Всего студентов: 0" in students_response.content.decode()
    assert "Студенты не найдены" in students_response.content.decode()
    assert "Всего задолженностей: 0" in debts_response.content.decode()
    assert "Задолженности не найдены" in debts_response.content.decode()


def test_database_pages_show_clean_students_and_statistics() -> None:
    client = Client()
    clean_response = client.get("/students/clean/")
    statistics_response = client.get("/debts/statistics/")

    assert clean_response.status_code == 200
    assert "Мария Волкова" in clean_response.content.decode()
    assert statistics_response.status_code == 200
    assert "Анна Смирнова" in statistics_response.content.decode()


@override_settings(DEBUG=False)
def test_unknown_url_uses_custom_404_page() -> None:
    response = Client().get("/nonexistent/")

    assert response.status_code == 404
    assert "Страница не найдена" in response.content.decode()
