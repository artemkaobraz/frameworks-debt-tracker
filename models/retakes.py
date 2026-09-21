from datetime import datetime
from typing import Any

from .debts import Debt


class Retake:
    def __init__(
        self, id: str, debt: Debt, retake_date: str,
        result: str | None = None,
    ) -> None:
        self.id = _required(id, "ID пересдачи")
        self.debt = debt
        self.retake_date = _validate_date(retake_date)
        self.result = result.strip() if result is not None else None

    def __str__(self) -> str:
        return (
            f"{self.debt.student.name}: {self.debt.discipline.name}, "
            f"{self.retake_date}"
        )

    @classmethod
    def from_data(
        cls, data: dict[str, Any], debts_by_id: dict[str, Debt]
    ) -> "Retake":
        result = data.get("result")
        return cls(
            str(data["id"]), debts_by_id[str(data["debt_id"])],
            str(data["retake_date"]),
            str(result) if result is not None else None,
        )

    def to_data(self) -> dict[str, Any]:
        return {
            "id": self.id, "debt_id": self.debt.id,
            "retake_date": self.retake_date, "result": self.result,
        }


def _required(value: object, field: str) -> str:
    result = str(value).strip()
    if not result:
        raise ValueError(f'Поле "{field}" не может быть пустым')
    return result


def _validate_date(value: str) -> str:
    result = value.strip()
    try:
        datetime.strptime(result, "%Y-%m-%d")
    except ValueError as error:
        raise ValueError("Дата должна быть в формате ГГГГ-ММ-ДД") from error
    return result


def _next_id(retakes: list[Retake]) -> str:
    ids = [int(item.id) for item in retakes if item.id.isdigit()]
    return str(max(ids, default=0) + 1)


def add_retake(
    retakes: list[Retake], debt: Debt, retake_date: str,
    result: str | None = None,
) -> Retake:
    if debt.is_closed:
        raise ValueError(
            "Для назначения пересдачи нужна активная задолженность"
        )
    normalized_date = _validate_date(retake_date)
    if any(
        item.debt.id == debt.id and item.retake_date == normalized_date
        for item in retakes
    ):
        raise ValueError("Такая пересдача уже существует")
    retake = Retake(_next_id(retakes), debt, normalized_date, result)
    retakes.append(retake)
    return retake


def cancel_retake(retakes: list[Retake], retake: Retake | str) -> bool:
    retake_id = retake.id if isinstance(retake, Retake) else str(retake)
    for index, saved_retake in enumerate(retakes):
        if saved_retake.id == retake_id:
            retakes.pop(index)
            return True
    return False


def count_retakes(student_id: object, retakes: list[Retake]) -> int:
    key = str(student_id).strip()
    return sum(1 for retake in retakes if retake.debt.student.id == key)


def get_student_retakes(
    student_id: object, retakes: list[Retake]
) -> list[Retake]:
    key = str(student_id).strip()
    matching = [
        retake for retake in retakes if retake.debt.student.id == key
    ]
    return sorted(matching, key=lambda retake: retake.retake_date)
