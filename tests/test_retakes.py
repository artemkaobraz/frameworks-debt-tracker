import pytest

from debts import add_debt
from retakes import add_retake
from retakes import cancel_retake
from retakes import count_retakes


def test_retake_requires_open_debt_and_can_be_cancelled() -> None:
    debts = []
    retakes = []

    with pytest.raises(ValueError):
        add_retake(retakes, debts, "1", "Математика", "2026-09-20")

    add_debt(debts, "1", "Математика", "2026-09-01")
    retake = add_retake(
        retakes,
        debts,
        "1",
        "Математика",
        "2026-09-20",
    )

    assert retake["retake_date"] == "2026-09-20"
    assert count_retakes("1", retakes) == 1
    assert cancel_retake(
        retakes,
        "1",
        "Математика",
        "2026-09-20",
    ) is True
    assert count_retakes("1", retakes) == 0
