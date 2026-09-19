from datetime import date
from typing import Any


Debt = dict[str, Any]
Student = dict[str, Any]
Students = dict[str, Student]


def _normalize_text(value: str, field_name: str) -> str:
    normalized_value = value.strip()
    if not normalized_value:
        raise ValueError(f'Поле "{field_name}" не может быть пустым')
    return normalized_value


def _same_discipline(first: object, second: str) -> bool:
    return str(first).casefold() == second.casefold()


def add_debt(
    debts: list[Debt],
    student_id: object,
    discipline: str,
    created_at: str | None = None,
) -> Debt:
    normalized_student_id = _normalize_text(str(student_id), "ID студента")
    normalized_discipline = _normalize_text(discipline, "Дисциплина")
    debt_date = created_at or date.today().isoformat()

    for debt in debts:
        if (
            str(debt.get("student_id")) == normalized_student_id
            and _same_discipline(
                debt.get("discipline", ""),
                normalized_discipline,
            )
            and debt.get("status") == "open"
        ):
            raise ValueError("Такая активная задолженность уже существует")

    debt = {
        "student_id": normalized_student_id,
        "discipline": normalized_discipline,
        "created_at": debt_date,
        "status": "open",
    }
    debts.append(debt)
    return debt


def close_debt(
    debts: list[Debt],
    student_id: object,
    discipline: str,
) -> bool:
    normalized_student_id = str(student_id).strip()
    normalized_discipline = discipline.strip()

    for debt in debts:
        if (
            str(debt.get("student_id")) == normalized_student_id
            and _same_discipline(
                debt.get("discipline", ""),
                normalized_discipline,
            )
            and debt.get("status") == "open"
        ):
            debt["status"] = "closed"
            debt["closed_at"] = date.today().isoformat()
            return True

    return False


def has_debt(
    debts: list[Debt],
    student_id: object,
    discipline: str | None = None,
) -> bool:
    normalized_student_id = str(student_id).strip()
    normalized_discipline = (
        discipline.strip() if discipline is not None else None
    )

    for debt in debts:
        if str(debt.get("student_id")) != normalized_student_id:
            continue
        if debt.get("status") != "open":
            continue
        if normalized_discipline is None:
            return True
        if _same_discipline(
            debt.get("discipline", ""),
            normalized_discipline,
        ):
            return True

    return False


def count_debts(
    student_id: object,
    debts: list[Debt],
    only_active: bool = True,
) -> int:
    normalized_student_id = str(student_id).strip()
    count = 0

    for debt in debts:
        if str(debt.get("student_id")) != normalized_student_id:
            continue
        if only_active and debt.get("status") != "open":
            continue
        count += 1

    return count


def has_more_than(
    student_id: object,
    num: int,
    debts: list[Debt],
) -> bool:
    return count_debts(student_id, debts) > num


def get_students_with_debts_more_than(
    students: Students,
    num: int,
    debts: list[Debt],
) -> list[str]:
    names = []

    for student_id, student in students.items():
        if has_more_than(student_id, num, debts):
            names.append(str(student.get("full_name", "")))

    return names


def get_worst_student(students: Students, debts: list[Debt]) -> str | None:
    worst_name = None
    highest_count = 0

    for student_id, student in students.items():
        debt_count = count_debts(student_id, debts)
        if debt_count > highest_count:
            highest_count = debt_count
            worst_name = str(student.get("full_name", ""))

    return worst_name


def get_debt_status(
    student_id: object,
    discipline: str,
    debts: list[Debt],
) -> str:
    normalized_student_id = str(student_id).strip()
    normalized_discipline = discipline.strip()
    found_closed = False

    for debt in debts:
        if (
            str(debt.get("student_id")) == normalized_student_id
            and _same_discipline(
                debt.get("discipline", ""),
                normalized_discipline,
            )
        ):
            if debt.get("status") == "open":
                return "open"
            if debt.get("status") == "closed":
                found_closed = True

    if found_closed:
        return "closed"
    return "not_found"


def filter_debts_by_discipline(
    debts: list[Debt],
    discipline: str,
    only_active: bool = True,
) -> list[Debt]:
    normalized_discipline = discipline.strip()
    result = []

    for debt in debts:
        if not _same_discipline(
            debt.get("discipline", ""),
            normalized_discipline,
        ):
            continue
        if only_active and debt.get("status") != "open":
            continue
        result.append(debt)

    return result
