from datetime import datetime
from typing import Any

from debts import has_debt


Retake = dict[str, Any]
Debt = dict[str, Any]


def _validate_date(date_value: str) -> str:
    normalized_date = date_value.strip()
    try:
        datetime.strptime(normalized_date, "%Y-%m-%d")
    except ValueError as error:
        raise ValueError("Дата должна быть в формате ГГГГ-ММ-ДД") from error
    return normalized_date


def add_retake(
    retakes: list[Retake],
    debts: list[Debt],
    student_id: object,
    discipline: str,
    retake_date: str,
) -> Retake:
    normalized_student_id = str(student_id).strip()
    normalized_discipline = discipline.strip()
    normalized_date = _validate_date(retake_date)

    if not normalized_student_id:
        raise ValueError("ID студента не может быть пустым")
    if not normalized_discipline:
        raise ValueError("Дисциплина не может быть пустой")
    if not has_debt(debts, normalized_student_id, normalized_discipline):
        raise ValueError(
            "Для назначения пересдачи нужна активная задолженность"
        )

    for retake in retakes:
        if (
            str(retake.get("student_id")) == normalized_student_id
            and str(retake.get("discipline", "")).casefold()
            == normalized_discipline.casefold()
            and retake.get("retake_date") == normalized_date
        ):
            raise ValueError("Такая пересдача уже существует")

    retake = {
        "student_id": normalized_student_id,
        "discipline": normalized_discipline,
        "retake_date": normalized_date,
    }
    retakes.append(retake)
    return retake


def cancel_retake(
    retakes: list[Retake],
    student_id: object,
    discipline: str,
    retake_date: str | None = None,
) -> bool:
    normalized_student_id = str(student_id).strip()
    normalized_discipline = discipline.strip().casefold()

    for index, retake in enumerate(retakes):
        if str(retake.get("student_id")) != normalized_student_id:
            continue
        saved_discipline = str(retake.get("discipline", "")).casefold()
        if saved_discipline != normalized_discipline:
            continue
        if (
            retake_date is not None
            and retake.get("retake_date") != retake_date
        ):
            continue
        retakes.pop(index)
        return True

    return False


def count_retakes(student_id: object, retakes: list[Retake]) -> int:
    normalized_student_id = str(student_id).strip()
    count = 0

    for retake in retakes:
        if str(retake.get("student_id")) == normalized_student_id:
            count += 1

    return count


def get_student_retakes(
    student_id: object,
    retakes: list[Retake],
) -> list[Retake]:
    normalized_student_id = str(student_id).strip()
    result = []

    for retake in retakes:
        if str(retake.get("student_id")) == normalized_student_id:
            result.append(retake)

    return sorted(result, key=lambda item: str(item.get("retake_date", "")))
