from typing import Any


Student = dict[str, Any]
Students = dict[str, Student]
Debt = dict[str, Any]


def _student_key(student_id: object) -> str:
    key = str(student_id).strip()
    if not key:
        raise ValueError("ID студента не может быть пустым")
    return key


def _student_with_id(student_id: str, student: Student) -> Student:
    result = dict(student)
    result["id"] = student_id
    return result


def add_student(
    students: Students,
    student_id: object,
    full_name: str,
    group: str,
) -> Student:
    key = _student_key(student_id)
    name = full_name.strip()
    group_name = group.strip()

    if key in students:
        raise ValueError(f"Студент с ID {key} уже существует")
    if not name:
        raise ValueError("ФИО студента не может быть пустым")
    if not group_name:
        raise ValueError("Группа студента не может быть пустой")

    student = {"full_name": name, "group": group_name}
    students[key] = student
    return student


def get_student(students: Students, student_id: object) -> Student:
    key = _student_key(student_id)
    try:
        return students[key]
    except KeyError as error:
        raise KeyError(f"Студент с ID {key} не найден") from error


def search_students(students: Students, query: str) -> list[Student]:
    normalized_query = query.strip().casefold()
    results = []

    for student_id, student in students.items():
        full_name = str(student.get("full_name", ""))
        if normalized_query in full_name.casefold():
            results.append(_student_with_id(student_id, student))

    return results


def students_with_debt_in_discipline(
    students: Students,
    debts: list[Debt],
    discipline: str,
) -> list[Student]:
    normalized_discipline = discipline.strip().casefold()
    student_ids = set()

    for debt in debts:
        debt_discipline = str(debt.get("discipline", "")).casefold()
        if (
            debt.get("status") == "open"
            and debt_discipline == normalized_discipline
        ):
            student_ids.add(str(debt.get("student_id", "")))

    return [
        _student_with_id(student_id, student)
        for student_id, student in students.items()
        if student_id in student_ids
    ]


def sort_students_by_debt_count(
    students: Students,
    debts: list[Debt],
    reverse: bool = True,
) -> list[Student]:
    debt_counts = {student_id: 0 for student_id in students}

    for debt in debts:
        student_id = str(debt.get("student_id", ""))
        if debt.get("status") == "open" and student_id in debt_counts:
            debt_counts[student_id] += 1

    result = []
    for student_id, student in students.items():
        item = _student_with_id(student_id, student)
        item["debt_count"] = debt_counts[student_id]
        result.append(item)

    result.sort(
        key=lambda item: (
            int(item["debt_count"]),
            str(item.get("full_name", "")).casefold(),
        ),
        reverse=reverse,
    )
    return result
