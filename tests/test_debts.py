import pytest

from debts import add_debt
from debts import close_debt
from debts import count_debts
from debts import get_debt_status
from debts import has_debt


def test_add_check_and_close_debt() -> None:
    debts = []

    debt = add_debt(debts, 1, "Математика", "2026-09-01")

    assert debt["status"] == "open"
    assert has_debt(debts, "1", "математика") is True
    assert get_debt_status("1", "Математика", debts) == "open"
    assert close_debt(debts, 1, "Математика") is True
    assert has_debt(debts, "1", "Математика") is False
    assert get_debt_status("1", "Математика", debts) == "closed"


def test_add_debt_rejects_active_duplicate() -> None:
    debts = []
    add_debt(debts, 1, "Математика")

    with pytest.raises(ValueError):
        add_debt(debts, "1", "математика")


def test_count_debts_can_include_closed_records() -> None:
    debts = [
        {
            "student_id": "1",
            "discipline": "Математика",
            "status": "open",
        },
        {"student_id": "1", "discipline": "Физика", "status": "closed"},
        {"student_id": "2", "discipline": "Химия", "status": "open"},
    ]

    assert count_debts("1", debts) == 1
    assert count_debts("1", debts, only_active=False) == 2
