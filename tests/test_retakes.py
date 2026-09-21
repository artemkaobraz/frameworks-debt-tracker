import pytest

from models import Debt, Discipline, Retake, Student
from models.retakes import add_retake
from models.retakes import cancel_retake
from models.retakes import count_retakes
from models.retakes import get_student_retakes


def test_retake_attributes_relation_and_string() -> None:
    student = Student("1", "Иванов Иван", "ПИ-21")
    discipline = Discipline("1", "Математика")
    debt = Debt("1", student, discipline, "2026-09-01")
    retake = Retake("1", debt, "2026-09-20", "сдано")
    assert retake.debt is debt
    assert retake.result == "сдано"
    assert "Математика" in str(retake)


def test_retake_collection_functions() -> None:
    student = Student("1", "Иванов Иван", "ПИ-21")
    discipline = Discipline("1", "Математика")
    debt = Debt("1", student, discipline, "2026-09-01")
    retakes = []
    retake = add_retake(retakes, debt, "2026-09-20")
    assert retake.debt is debt
    assert count_retakes("1", retakes) == 1
    assert get_student_retakes("1", retakes) == [retake]
    assert cancel_retake(retakes, retake) is True
    assert retakes == []


def test_retake_requires_open_debt() -> None:
    student = Student("1", "Иванов Иван", "ПИ-21")
    discipline = Discipline("1", "Математика")
    debt = Debt("1", student, discipline, "2026-09-01", True)
    with pytest.raises(ValueError):
        add_retake([], debt, "2026-09-20")
