from django.test import Client
from django.test import override_settings


def test_homepage_has_navigation() -> None:
    response = Client().get("/")

    assert response.status_code == 200
    assert "DebtTrack" in response.content.decode()
    assert "/disciplines/" in response.content.decode()


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


def test_missing_objects_return_404() -> None:
    client = Client()

    assert client.get("/students/999/").status_code == 404
    assert client.get("/debts/999/").status_code == 404


@override_settings(DEBUG=False)
def test_unknown_url_uses_custom_404_page() -> None:
    response = Client().get("/nonexistent/")

    assert response.status_code == 404
    assert "Страница не найдена" in response.content.decode()
