from typing import Any


class Student:
    def __init__(
        self,
        id: str,
        name: str,
        group_number: str,
        record_book: str = "",
    ) -> None:
        self.id = _required_text(id, "ID студента")
        self.name = _required_text(name, "ФИО студента")
        self.group_number = _required_text(group_number, "Группа студента")
        self.record_book = record_book.strip()

    def __str__(self) -> str:
        return f"{self.name} ({self.group_number})"

    @classmethod
    def from_data(
        cls,
        data: dict[str, Any],
        student_id: str | None = None,
    ) -> "Student":
        return cls(
            id=student_id if student_id is not None else str(data["id"]),
            name=str(data.get("name", data.get("full_name", ""))),
            group_number=str(data.get("group_number", data.get("group", ""))),
            record_book=str(data.get("record_book", "")),
        )

    def to_data(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "group_number": self.group_number,
            "record_book": self.record_book,
        }


def _required_text(value: object, field_name: str) -> str:
    normalized_value = str(value).strip()
    if not normalized_value:
        raise ValueError(f'Поле "{field_name}" не может быть пустым')
    return normalized_value


def add_student(
    students: list[Student],
    student_id: object,
    full_name: str,
    group: str,
    record_book: str = "",
) -> Student:
    normalized_id = _required_text(student_id, "ID студента")
    if any(student.id == normalized_id for student in students):
        raise ValueError(f"Студент с ID {normalized_id} уже существует")
    student = Student(normalized_id, full_name, group, record_book)
    students.append(student)
    return student


def get_student(students: list[Student], student_id: object) -> Student:
    normalized_id = _required_text(student_id, "ID студента")
    for student in students:
        if student.id == normalized_id:
            return student
    raise KeyError(f"Студент с ID {normalized_id} не найден")


def search_students(students: list[Student], query: str) -> list[Student]:
    normalized_query = query.strip().casefold()
    return [
        student
        for student in students
        if normalized_query in student.name.casefold()
    ]


def students_with_debt_in_discipline(
    students: list[Student],
    debts: list[Any],
    discipline: str,
) -> list[Student]:
    normalized_discipline = discipline.strip().casefold()
    student_ids = {
        debt.student.id
        for debt in debts
        if not debt.is_closed
        and debt.discipline.name.casefold() == normalized_discipline
    }
    return [student for student in students if student.id in student_ids]


def sort_students_by_debt_count(
    students: list[Student],
    debts: list[Any],
    reverse: bool = True,
) -> list[Student]:
    debt_counts = {
        student.id: sum(
            1
            for debt in debts
            if debt.student.id == student.id and not debt.is_closed
        )
        for student in students
    }
    return sorted(
        students,
        key=lambda student: (
            debt_counts[student.id],
            student.name.casefold(),
        ),
        reverse=reverse,
    )
