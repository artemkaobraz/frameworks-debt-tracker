import pytest

from models import Discipline, Student
from models.debts import add_debt
from models.students import add_student
from models.students import search_students
from models.students import sort_students_by_debt_count
from models.students import students_with_debt_in_discipline


def test_student_attributes_string_and_add() -> None:
    students = []
    student = add_student(students, 1, "Иванов Иван", "ПИ-21", "123")
    assert student.id == "1"
    assert student.name == "Иванов Иван"
    assert student.group_number == "ПИ-21"
    assert student.record_book == "123"
    assert str(student) == "Иванов Иван (ПИ-21)"
    assert students == [student]


def test_add_student_rejects_duplicate_id() -> None:
    students = [Student("1", "Иванов Иван", "ПИ-21")]
    with pytest.raises(ValueError):
        add_student(students, "1", "Петров Пётр", "ПИ-22")


def test_student_collection_functions() -> None:
    first = Student("1", "Иванов Иван", "ПИ-21")
    second = Student("2", "Петров Пётр", "ПИ-22")
    students = [first, second]
    math = Discipline("1", "Математика")
    physics = Discipline("2", "Физика")
    debts = []
    add_debt(debts, first, math)
    add_debt(debts, first, physics)
    assert search_students(students, "иВаНоВ") == [first]
    assert students_with_debt_in_discipline(
        students, debts, "математика"
    ) == [first]
    assert sort_students_by_debt_count(students, debts) == [first, second]
