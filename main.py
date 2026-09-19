from pathlib import Path
from typing import Any

from debts import (
    add_debt,
    close_debt,
    count_debts,
    get_debt_status,
    get_students_with_debts_more_than,
    get_worst_student,
    has_debt,
    has_more_than,
)
from retakes import (
    add_retake,
    cancel_retake,
    count_retakes,
    get_student_retakes,
)
from storage import load_data, save_debts, save_retakes, save_students
from students import (
    add_student,
    get_student,
    search_students,
    sort_students_by_debt_count,
    students_with_debt_in_discipline,
)
from utils import input_date, input_int

DATA_DIR = Path(__file__).parent / "data"

MENU_OPTIONS = (
    "Просмотреть студентов",
    "Добавить студента",
    "Найти студента по ФИО",
    "Добавить задолженность",
    "Закрыть задолженность",
    "Найти должников по дисциплине",
    "Отсортировать студентов "
    "по количеству задолженностей",
    "Показать статистику студента",
    "Добавить пересдачу",
    "Отменить пересдачу",
    "Выход",
)


def _print_student(student_id: str, student: dict[str, Any]) -> None:
    full_name = student.get("full_name", "Без имени")
    group = student.get("group", "Не указана")
    print(f"{student_id}: {full_name}, группа {group}")


def _print_students(
    students: dict[str, dict[str, Any]] | list[dict[str, Any]],
) -> None:
    if not students:
        print("Студенты не найдены.")
        return

    if isinstance(students, dict):
        for student_id, student in students.items():
            _print_student(student_id, student)
        return

    for student in students:
        student_id = str(student.get("id", "Не указан"))
        _print_student(student_id, student)


def _require_student(
    students: dict[str, dict[str, Any]], student_id: str
) -> dict[str, Any]:
    student = get_student(students, student_id)
    if student is None:
        raise KeyError(f"Студент с id {student_id} не найден")
    return student


def _show_menu() -> None:
    print("Учёт академических задолженностей")
    for index in range(len(MENU_OPTIONS)):
        print(f"{index + 1}. {MENU_OPTIONS[index]}")


def _show_sorted_students(
    students: dict[str, dict[str, Any]], debts: list[dict[str, Any]]
) -> None:
    sorted_students = sort_students_by_debt_count(
        students, debts, reverse=True
    )
    if not sorted_students:
        print("Студенты не найдены.")
        return

    for student in sorted_students:
        student_id = str(student.get("id", "Не указан"))
        debt_total = student.get("debt_count", count_debts(student_id, debts))
        _print_student(student_id, student)
        print(f"  Активных задолженностей: {debt_total}")


def _show_statistics(
    students: dict[str, dict[str, Any]],
    debts: list[dict[str, Any]],
    retakes: list[dict[str, Any]],
) -> None:
    student_id = input("ID студента: ").strip()
    student = _require_student(students, student_id)
    _print_student(student_id, student)
    debt_total = count_debts(student_id, debts)
    print(f"Активных задолженностей: {debt_total}")
    print(f"Всего пересдач: {count_retakes(student_id, retakes)}")

    student_retakes = get_student_retakes(student_id, retakes)
    if student_retakes:
        print("Пересдачи:")
        for retake in student_retakes:
            discipline = retake.get("discipline", "Не указана")
            retake_date = retake.get("retake_date", retake.get("date", ""))
            print(f"- {discipline}: {retake_date}")


def run_application() -> None:
    try:
        students, debts, retakes = load_data(DATA_DIR)
    except OSError:
        print("Не удалось загрузить данные из файлов.")
        print(
            "Работа начата с пустыми "
            "коллекциями."
        )
        students, debts, retakes = {}, [], []
    except ValueError as error:
        print(f"Не удалось загрузить данные: {error}")
        print(
            "Работа начата с пустыми "
            "коллекциями."
        )
        students, debts, retakes = {}, [], []

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
                full_name = input("ФИО: ").strip()
                group = input("Группа: ").strip()
                add_student(students, student_id, full_name, group)
                save_students(students, DATA_DIR)
                print("Студент добавлен.")

            elif choice == 3:
                query = input("Часть ФИО: ").strip()
                _print_students(search_students(students, query))

            elif choice == 4:
                student_id = input("ID студента: ").strip()
                _require_student(students, student_id)
                discipline = input("Дисциплина: ").strip()
                add_debt(debts, student_id, discipline)
                save_debts(debts, DATA_DIR)
                print("Задолженность добавлена.")

            elif choice == 5:
                student_id = input("ID студента: ").strip()
                _require_student(students, student_id)
                discipline = input("Дисциплина: ").strip()
                if close_debt(debts, student_id, discipline):
                    save_debts(debts, DATA_DIR)
                    print("Задолженность закрыта.")
                else:
                    print(
                        "Открытая задолженность "
                        "не найдена."
                    )

            elif choice == 6:
                discipline = input("Дисциплина: ").strip()
                result = students_with_debt_in_discipline(
                    students, debts, discipline
                )
                _print_students(result)

            elif choice == 7:
                _show_sorted_students(students, debts)

            elif choice == 8:
                _show_statistics(students, debts, retakes)

            elif choice == 9:
                student_id = input("ID студента: ").strip()
                _require_student(students, student_id)
                discipline = input("Дисциплина: ").strip()
                if get_debt_status(student_id, discipline, debts) != "open":
                    print(
                        "Для пересдачи нужна "
                        "открытая "
                        "задолженность."
                    )
                    continue
                retake_date = input_date(
                    "Дата пересдачи (ГГГГ-ММ-ДД): "
                )
                add_retake(
                    retakes, debts, student_id, discipline, retake_date
                )
                save_retakes(retakes, DATA_DIR)
                print("Пересдача добавлена.")

            elif choice == 10:
                student_id = input("ID студента: ").strip()
                _require_student(students, student_id)
                discipline = input("Дисциплина: ").strip()
                retake_date = input_date(
                    "Дата пересдачи (ГГГГ-ММ-ДД): "
                )
                if cancel_retake(
                    retakes, student_id, discipline, retake_date
                ):
                    save_retakes(retakes, DATA_DIR)
                    print("Пересдача отменена.")
                else:
                    print("Пересдача не найдена.")

        except ValueError as error:
            print(f"Некорректные данные: {error}")
        except KeyError as error:
            message = (
                error.args[0]
                if error.args
                else "Данные не найдены."
            )
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
