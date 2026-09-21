import copy
import json
from pathlib import Path
from typing import Any, TypeVar

from models.debts import Debt
from models.disciplines import Discipline
from models.retakes import Retake
from models.students import Student


DEFAULT_DATA_DIR = Path("data")
STUDENTS_FILE = "students.json"
DISCIPLINES_FILE = "disciplines.json"
DEBTS_FILE = "debts.json"
RETAKES_FILE = "retakes.json"

T = TypeVar("T")


def load_json(path: str | Path, default: T) -> T:
    file_path = Path(path)
    try:
        with file_path.open("r", encoding="utf-8") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return copy.deepcopy(default)
    except json.JSONDecodeError as error:
        raise ValueError(f"Некорректный JSON в файле: {file_path}") from error


def save_json(path: str | Path, data: Any) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)
        json_file.write("\n")


def _require_dict(data: object, path: Path) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError(f"{path}: ожидался объект JSON")
    return data


def _require_list(data: object, path: Path) -> list[Any]:
    if not isinstance(data, list):
        raise ValueError(f"{path}: ожидался массив JSON")
    return data


def _require_item(data: object, path: Path) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError(f"{path}: элементы массива должны быть объектами")
    return data


def _make_student(student_id: str, data: object, path: Path) -> Student:
    item = _require_item(data, path)
    name = item.get("name", item.get("full_name"))
    group_number = item.get("group_number", item.get("group"))
    if not isinstance(name, str) or not isinstance(group_number, str):
        raise ValueError(f"{path}: некорректные данные студента")
    try:
        return Student(
            student_id,
            name,
            group_number,
            item.get("record_book", ""),
        )
    except (TypeError, ValueError) as error:
        raise ValueError(f"{path}: некорректные данные студента") from error


def _make_discipline(data: object, path: Path) -> Discipline:
    item = _require_item(data, path)
    try:
        return Discipline(
            str(item["id"]),
            item["name"],
            item.get("teacher", ""),
            item.get("semester", 0),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"{path}: некорректные данные дисциплины") from error


def _legacy_discipline_names(
    debts_data: list[Any],
    retakes_data: list[Any],
    path: Path,
) -> list[str]:
    names: list[str] = []
    for raw_item in debts_data + retakes_data:
        item = _require_item(raw_item, path)
        name = item.get("discipline")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"{path}: не указана дисциплина")
        if name not in names:
            names.append(name)
    return names


def load_data(
    data_dir: str | Path = DEFAULT_DATA_DIR,
) -> tuple[list[Student], list[Discipline], list[Debt], list[Retake]]:
    directory = Path(data_dir)
    students_path = directory / STUDENTS_FILE
    disciplines_path = directory / DISCIPLINES_FILE
    debts_path = directory / DEBTS_FILE
    retakes_path = directory / RETAKES_FILE
    students_data = _require_dict(load_json(students_path, {}), students_path)
    disciplines_data = _require_list(
        load_json(disciplines_path, []), disciplines_path
    )
    debts_data = _require_list(load_json(debts_path, []), debts_path)
    retakes_data = _require_list(load_json(retakes_path, []), retakes_path)

    students = [
        _make_student(str(student_id), data, students_path)
        for student_id, data in students_data.items()
    ]
    students_by_id = {student.id: student for student in students}
    if disciplines_data:
        disciplines = [
            _make_discipline(data, disciplines_path)
            for data in disciplines_data
        ]
    else:
        names = _legacy_discipline_names(
            debts_data, retakes_data, disciplines_path
        )
        disciplines = [
            Discipline(str(index), name, "", 0)
            for index, name in enumerate(names, start=1)
        ]
    disciplines_by_id = {
        discipline.id: discipline for discipline in disciplines
    }
    disciplines_by_name = {
        discipline.name: discipline for discipline in disciplines
    }

    debts: list[Debt] = []
    for index, raw_data in enumerate(debts_data, start=1):
        data = _require_item(raw_data, debts_path)
        student = students_by_id.get(str(data.get("student_id", "")))
        discipline_id = data.get("discipline_id")
        if discipline_id is not None:
            discipline = disciplines_by_id.get(str(discipline_id))
        else:
            discipline = disciplines_by_name.get(
                str(data.get("discipline", ""))
            )
        if student is None or discipline is None:
            raise ValueError(f"{debts_path}: найдена недействительная ссылка")
        date_created = data.get("date_created", data.get("created_at"))
        if not isinstance(date_created, str):
            raise ValueError(f"{debts_path}: не указана дата задолженности")
        is_closed = data.get("is_closed", data.get("status") == "closed")
        if not isinstance(is_closed, bool):
            raise ValueError(
                f"{debts_path}: некорректный статус задолженности"
            )
        debts.append(
            Debt(
                str(data.get("id", index)),
                student,
                discipline,
                date_created,
                is_closed,
                data.get("closed_at"),
            )
        )
    debts_by_id = {debt.id: debt for debt in debts}

    retakes: list[Retake] = []
    for index, raw_data in enumerate(retakes_data, start=1):
        data = _require_item(raw_data, retakes_path)
        debt_id = data.get("debt_id")
        if debt_id is not None:
            debt = debts_by_id.get(str(debt_id))
        else:
            student_id = str(data.get("student_id", ""))
            discipline_name = str(data.get("discipline", ""))
            debt = next(
                (
                    item
                    for item in debts
                    if item.student.id == student_id
                    and item.discipline.name == discipline_name
                ),
                None,
            )
        if debt is None:
            raise ValueError(
                f"{retakes_path}: найдена недействительная ссылка"
            )
        retake_date = data.get("retake_date")
        if not isinstance(retake_date, str):
            raise ValueError(f"{retakes_path}: не указана дата пересдачи")
        retakes.append(
            Retake(
                str(data.get("id", index)),
                debt,
                retake_date,
                data.get("result"),
            )
        )

    return students, disciplines, debts, retakes


def save_students(
    students: list[Student],
    data_dir: str | Path = DEFAULT_DATA_DIR,
) -> None:
    data = {
        student.id: {
            "name": student.name,
            "group_number": student.group_number,
            "record_book": student.record_book,
        }
        for student in students
    }
    save_json(Path(data_dir) / STUDENTS_FILE, data)


def save_disciplines(
    disciplines: list[Discipline],
    data_dir: str | Path = DEFAULT_DATA_DIR,
) -> None:
    save_json(
        Path(data_dir) / DISCIPLINES_FILE,
        [discipline.to_data() for discipline in disciplines],
    )


def save_debts(
    debts: list[Debt],
    data_dir: str | Path = DEFAULT_DATA_DIR,
) -> None:
    save_json(
        Path(data_dir) / DEBTS_FILE,
        [debt.to_data() for debt in debts],
    )


def save_retakes(
    retakes: list[Retake],
    data_dir: str | Path = DEFAULT_DATA_DIR,
) -> None:
    save_json(
        Path(data_dir) / RETAKES_FILE,
        [retake.to_data() for retake in retakes],
    )


def save_data(
    data_dir: str | Path,
    students: list[Student],
    disciplines: list[Discipline],
    debts: list[Debt],
    retakes: list[Retake],
) -> None:
    save_students(students, data_dir)
    save_disciplines(disciplines, data_dir)
    save_debts(debts, data_dir)
    save_retakes(retakes, data_dir)
