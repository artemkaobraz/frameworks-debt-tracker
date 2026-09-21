from datetime import date
from typing import Any

from .disciplines import Discipline
from .students import Student


class Debt:
    def __init__(
        self,
        id: str,
        student: Student,
        discipline: Discipline,
        date_created: str,
        is_closed: bool = False,
        closed_at: str | None = None,
    ) -> None:
        self.id = _required(id, "ID задолженности")
        self.student = student
        self.discipline = discipline
        self.date_created = _required(date_created, "Дата создания")
        self.is_closed = bool(is_closed)
        self.closed_at = closed_at

    def __str__(self) -> str:
        status = "закрыта" if self.is_closed else "открыта"
        return f"{self.student.name}: {self.discipline.name} ({status})"

    def close(self) -> None:
        if self.is_closed:
            raise ValueError("Задолженность уже закрыта")
        self.is_closed = True
        self.closed_at = date.today().isoformat()

    @classmethod
    def from_data(
        cls,
        data: dict[str, Any],
        students_by_id: dict[str, Student],
        disciplines_by_id: dict[str, Discipline],
    ) -> "Debt":
        status = data.get("status")
        closed_at = data.get("closed_at")
        return cls(
            str(data["id"]),
            students_by_id[str(data["student_id"])],
            disciplines_by_id[str(data["discipline_id"])],
            str(data.get("date_created", data.get("created_at", ""))),
            bool(data.get("is_closed", status == "closed")),
            str(closed_at) if closed_at is not None else None,
        )

    def to_data(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "student_id": self.student.id,
            "discipline_id": self.discipline.id,
            "date_created": self.date_created,
            "is_closed": self.is_closed,
            "closed_at": self.closed_at,
        }


def _required(value: object, field: str) -> str:
    result = str(value).strip()
    if not result:
        raise ValueError(f'Поле "{field}" не может быть пустым')
    return result


def _next_id(debts: list[Debt]) -> str:
    ids = [int(item.id) for item in debts if item.id.isdigit()]
    return str(max(ids, default=0) + 1)


def add_debt(
    debts: list[Debt],
    student: Student,
    discipline: Discipline,
    created_at: str | None = None,
) -> Debt:
    if any(
        item.student.id == student.id
        and item.discipline.id == discipline.id
        and not item.is_closed
        for item in debts
    ):
        raise ValueError("Такая активная задолженность уже существует")
    debt = Debt(
        _next_id(debts),
        student,
        discipline,
        created_at or date.today().isoformat(),
    )
    debts.append(debt)
    return debt


def close_debt(debt: Debt) -> bool:
    debt.close()
    return True


def _student_id(student: Student | str) -> str:
    return student.id if isinstance(student, Student) else str(student).strip()


def has_debt(
    debts: list[Debt],
    student: Student | str,
    discipline: Discipline | str | None = None,
) -> bool:
    for debt in debts:
        if debt.student.id != _student_id(student) or debt.is_closed:
            continue
        if discipline is None:
            return True
        if (
            isinstance(discipline, Discipline)
            and debt.discipline.id == discipline.id
        ):
            return True
        if (
            isinstance(discipline, str)
            and debt.discipline.name.casefold()
            == discipline.strip().casefold()
        ):
            return True
    return False


def count_debts(
    student: Student | str,
    debts: list[Debt],
    only_active: bool = True,
) -> int:
    return sum(
        1
        for debt in debts
        if debt.student.id == _student_id(student)
        and (not only_active or not debt.is_closed)
    )


def has_more_than(
    student: Student | str,
    num: int,
    debts: list[Debt],
) -> bool:
    return count_debts(student, debts) > num


def get_students_with_debts_more_than(
    students: list[Student],
    num: int,
    debts: list[Debt],
) -> list[str]:
    return [
        student.name
        for student in students
        if has_more_than(student, num, debts)
    ]


def get_worst_student(
    students: list[Student],
    debts: list[Debt],
) -> str | None:
    if not students:
        return None
    worst = max(students, key=lambda student: count_debts(student, debts))
    return worst.name if count_debts(worst, debts) else None


def get_debt_status(
    student: Student | str,
    discipline: Discipline | str,
    debts: list[Debt],
) -> str:
    matching = filter_debts_by_discipline(debts, discipline, False)
    matching = [
        item
        for item in matching
        if item.student.id == _student_id(student)
    ]
    if any(not item.is_closed for item in matching):
        return "open"
    return "closed" if matching else "not_found"


def filter_debts_by_discipline(
    debts: list[Debt],
    discipline: Discipline | str,
    only_active: bool = True,
) -> list[Debt]:
    def matches(debt: Debt) -> bool:
        if isinstance(discipline, Discipline):
            return debt.discipline.id == discipline.id
        return debt.discipline.name.casefold() == discipline.strip().casefold()
    return [
        debt
        for debt in debts
        if matches(debt) and (not only_active or not debt.is_closed)
    ]
