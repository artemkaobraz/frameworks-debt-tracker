import pytest

from models import Debt, Discipline, Student
from models.debts import add_debt
from models.debts import close_debt
from models.debts import count_debts
from models.debts import get_debt_status
from models.debts import get_students_with_debts_more_than
from models.debts import get_worst_student
from models.debts import has_debt


def test_debt_attributes_relations_string_and_close() -> None:
    student = Student("1", "Иванов Иван", "ПИ-21")
    discipline = Discipline("1", "Математика")
    debt = Debt("1", student, discipline, "2026-09-01")
    assert debt.student is student
    assert debt.discipline is discipline
    assert "Иванов Иван" in str(debt)
    debt.close()
    assert debt.is_closed is True
    assert debt.closed_at is not None
    with pytest.raises(ValueError):
        debt.close()


def test_add_check_and_close_debt() -> None:
    student = Student("1", "Иванов Иван", "ПИ-21")
    discipline = Discipline("1", "Математика")
    debts = []
    debt = add_debt(debts, student, discipline, "2026-09-01")
    assert has_debt(debts, student, discipline) is True
    assert get_debt_status(student, discipline, debts) == "open"
    assert close_debt(debt) is True
    assert get_debt_status(student, discipline, debts) == "closed"
    with pytest.raises(ValueError):
        close_debt(debt)


def test_debt_collection_statistics() -> None:
    first = Student("1", "Иванов Иван", "ПИ-21")
    second = Student("2", "Петров Пётр", "ПИ-22")
    math = Discipline("1", "Математика")
    physics = Discipline("2", "Физика")
    debts = [
        Debt("1", first, math, "2026-09-01"),
        Debt("2", first, physics, "2026-09-02", True),
        Debt("3", second, math, "2026-09-03"),
    ]
    assert count_debts(first, debts) == 1
    assert count_debts(first, debts, only_active=False) == 2
    assert get_worst_student([first, second], debts) == "Иванов Иван"
    assert get_students_with_debts_more_than(
        [first, second], 0, debts
    ) == ["Иванов Иван", "Петров Пётр"]
