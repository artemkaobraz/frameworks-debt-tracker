import pytest

from students import add_student
from students import search_students
from students import sort_students_by_debt_count
from students import students_with_debt_in_discipline


def test_add_student() -> None:
    students = {}

    student = add_student(students, 1, "Иванов Иван", "ПИ-21")

    assert student == {
        "full_name": "Иванов Иван",
        "group": "ПИ-21",
    }
    assert students["1"] == student


def test_add_student_rejects_duplicate_id() -> None:
    students = {
        "1": {"full_name": "Иванов Иван", "group": "ПИ-21"},
    }

    with pytest.raises(ValueError):
        add_student(students, "1", "Петров Пётр", "ПИ-22")


def test_search_students_is_case_insensitive() -> None:
    students = {
        "1": {"full_name": "Иванов Иван", "group": "ПИ-21"},
        "2": {"full_name": "Петров Пётр", "group": "ПИ-22"},
    }

    result = search_students(students, "иВаНоВ")

    assert result == [
        {"id": "1", "full_name": "Иванов Иван", "group": "ПИ-21"}
    ]


def test_filter_and_sort_students_by_open_debts() -> None:
    students = {
        "1": {"full_name": "Иванов Иван", "group": "ПИ-21"},
        "2": {"full_name": "Петров Пётр", "group": "ПИ-22"},
    }
    debts = [
        {
            "student_id": "1",
            "discipline": "Математика",
            "status": "open",
        },
        {"student_id": "1", "discipline": "Физика", "status": "open"},
        {
            "student_id": "2",
            "discipline": "Математика",
            "status": "closed",
        },
    ]

    filtered = students_with_debt_in_discipline(
        students,
        debts,
        "математика",
    )
    sorted_students = sort_students_by_debt_count(students, debts)

    assert [student["id"] for student in filtered] == ["1"]
    assert [student["id"] for student in sorted_students] == ["1", "2"]
    assert [
        student["debt_count"] for student in sorted_students
    ] == [2, 0]
