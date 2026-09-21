from pathlib import Path

from models import Debt, Discipline, Retake, Student
from models.debts import (
    add_debt,
    close_debt,
    count_debts,
    filter_debts_by_discipline,
    get_students_with_debts_more_than,
    get_worst_student,
    has_debt,
    has_more_than,
)
from models.disciplines import add_discipline
from models.retakes import (
    add_retake,
    cancel_retake,
    count_retakes,
    get_student_retakes,
)
from models.students import (
    add_student,
    get_student,
    search_students,
    sort_students_by_debt_count,
    students_with_debt_in_discipline,
)
from storage import load_data, save_data
from utils import input_date, input_int


DATA_DIR = Path(__file__).parent / "data"

MENU_OPTIONS = (
    "Просмотреть студентов",
    "Добавить студента",
    "Найти студента по ФИО",
    "Добавить задолженность",
    "Закрыть задолженность",
    "Найти должников по дисциплине",
    "Отсортировать студентов по количеству задолженностей",
    "Показать статистику студента",
    "Добавить пересдачу",
    "Отменить пересдачу",
    "Выход",
)


def _print_student(student: Student) -> None:
    print(f"{student.id}: {student.name}, группа {student.group_number}")


def _print_students(students: list[Student]) -> None:
    if not students:
        print("Студенты не найдены.")
        return
    for student in students:
        _print_student(student)


def _show_menu() -> None:
    print("Учёт академических задолженностей")
    for index, option in enumerate(MENU_OPTIONS, start=1):
        print(f"{index}. {option}")


def _next_discipline_id(disciplines: list[Discipline]) -> str:
    numeric_ids = [
        int(discipline.id)
        for discipline in disciplines
        if discipline.id.isdigit()
    ]
    return str(max(numeric_ids, default=0) + 1)


def _find_discipline(
    disciplines: list[Discipline],
    name: str,
) -> Discipline | None:
    normalized_name = name.strip().casefold()
    for discipline in disciplines:
        if discipline.name.casefold() == normalized_name:
            return discipline
    return None


def _get_or_create_discipline(
    disciplines: list[Discipline],
) -> Discipline:
    name = input("Дисциплина: ").strip()
    discipline = _find_discipline(disciplines, name)
    if discipline is not None:
        return discipline
    teacher = input("Преподаватель: ").strip()
    semester = input_int("Семестр: ")
    return add_discipline(
        disciplines,
        _next_discipline_id(disciplines),
        name,
        teacher,
        semester,
    )


def _find_open_debt(
    debts: list[Debt],
    student: Student,
    discipline_name: str,
) -> Debt | None:
    for debt in filter_debts_by_discipline(debts, discipline_name):
        if debt.student.id == student.id:
            return debt
    return None


def _show_sorted_students(
    students: list[Student],
    debts: list[Debt],
) -> None:
    sorted_students = sort_students_by_debt_count(students, debts)
    if not sorted_students:
        print("Студенты не найдены.")
        return
    for student in sorted_students:
        _print_student(student)
        print(f"  Активных задолженностей: {count_debts(student, debts)}")


def _show_statistics(
    students: list[Student],
    debts: list[Debt],
    retakes: list[Retake],
) -> None:
    student = get_student(students, input("ID студента: ").strip())
    _print_student(student)
    print(f"Активных задолженностей: {count_debts(student, debts)}")
    print(f"Всего пересдач: {count_retakes(student.id, retakes)}")
    student_retakes = get_student_retakes(student.id, retakes)
    if student_retakes:
        print("Пересдачи:")
        for retake in student_retakes:
            print(
                f"- {retake.debt.discipline.name}: {retake.retake_date}"
            )


def _save(
    students: list[Student],
    disciplines: list[Discipline],
    debts: list[Debt],
    retakes: list[Retake],
) -> None:
    save_data(DATA_DIR, students, disciplines, debts, retakes)


def run_application() -> None:
    try:
        students, disciplines, debts, retakes = load_data(DATA_DIR)
    except (OSError, ValueError) as error:
        print(f"Не удалось загрузить данные: {error}")
        print("Работа начата с пустыми коллекциями.")
        students, disciplines, debts, retakes = [], [], [], []

    while True:
        _show_menu()
        choice = input_int("Выберите пункт: ")
        if choice < 1 or choice > len(MENU_OPTIONS):
            print("Такого пункта меню нет.")
            continue
        if choice == len(MENU_OPTIONS):
            break

        try:
            if choice == 1:
                _print_students(students)
            elif choice == 2:
                student_id = input("ID студента: ").strip()
                name = input("ФИО: ").strip()
                group_number = input("Группа: ").strip()
                record_book = input("Номер зачётной книжки: ").strip()
                add_student(
                    students,
                    student_id,
                    name,
                    group_number,
                    record_book,
                )
                _save(students, disciplines, debts, retakes)
                print("Студент добавлен.")
            elif choice == 3:
                query = input("Часть ФИО: ").strip()
                _print_students(search_students(students, query))
            elif choice == 4:
                student = get_student(
                    students, input("ID студента: ").strip()
                )
                discipline = _get_or_create_discipline(disciplines)
                add_debt(debts, student, discipline)
                _save(students, disciplines, debts, retakes)
                print("Задолженность добавлена.")
            elif choice == 5:
                student = get_student(
                    students, input("ID студента: ").strip()
                )
                discipline_name = input("Дисциплина: ").strip()
                debt = _find_open_debt(debts, student, discipline_name)
                if debt is None:
                    print("Открытая задолженность не найдена.")
                else:
                    close_debt(debt)
                    _save(students, disciplines, debts, retakes)
                    print("Задолженность закрыта.")
            elif choice == 6:
                discipline_name = input("Дисциплина: ").strip()
                _print_students(
                    students_with_debt_in_discipline(
                        students, debts, discipline_name
                    )
                )
            elif choice == 7:
                _show_sorted_students(students, debts)
            elif choice == 8:
                _show_statistics(students, debts, retakes)
            elif choice == 9:
                student = get_student(
                    students, input("ID студента: ").strip()
                )
                discipline_name = input("Дисциплина: ").strip()
                debt = _find_open_debt(debts, student, discipline_name)
                if debt is None:
                    print("Для пересдачи нужна открытая задолженность.")
                    continue
                retake_date = input_date(
                    "Дата пересдачи (ГГГГ-ММ-ДД): "
                )
                add_retake(retakes, debt, retake_date)
                _save(students, disciplines, debts, retakes)
                print("Пересдача добавлена.")
            elif choice == 10:
                student = get_student(
                    students, input("ID студента: ").strip()
                )
                discipline_name = input("Дисциплина: ").strip()
                retake_date = input_date(
                    "Дата пересдачи (ГГГГ-ММ-ДД): "
                )
                retake = next(
                    (
                        item
                        for item in retakes
                        if item.debt.student.id == student.id
                        and item.debt.discipline.name.casefold()
                        == discipline_name.casefold()
                        and item.retake_date == retake_date
                    ),
                    None,
                )
                if retake is None or not cancel_retake(retakes, retake):
                    print("Пересдача не найдена.")
                else:
                    _save(students, disciplines, debts, retakes)
                    print("Пересдача отменена.")
        except ValueError as error:
            print(f"Некорректные данные: {error}")
        except KeyError as error:
            message = error.args[0] if error.args else "Данные не найдены."
            print(message)
        except OSError:
            print("Не удалось сохранить данные в файл.")


__all__ = [
    "add_debt",
    "close_debt",
    "count_debts",
    "get_students_with_debts_more_than",
    "get_worst_student",
    "has_debt",
    "has_more_than",
    "run_application",
]


if __name__ == "__main__":
    run_application()
