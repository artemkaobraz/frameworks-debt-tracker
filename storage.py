import copy
import json
from pathlib import Path
from typing import Any, TypeVar


DEFAULT_DATA_DIR = Path("data")
STUDENTS_FILE = "students.json"
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


def load_data(
    data_dir: str | Path = DEFAULT_DATA_DIR,
) -> tuple[
    dict[str, dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    directory = Path(data_dir)
    students = load_json(directory / STUDENTS_FILE, {})
    debts = load_json(directory / DEBTS_FILE, [])
    retakes = load_json(directory / RETAKES_FILE, [])

    if not isinstance(students, dict):
        raise ValueError(
            f"{directory / STUDENTS_FILE}: ожидался объект JSON"
        )
    if not isinstance(debts, list):
        raise ValueError(
            f"{directory / DEBTS_FILE}: ожидался массив JSON"
        )
    if not isinstance(retakes, list):
        raise ValueError(
            f"{directory / RETAKES_FILE}: ожидался массив JSON"
        )

    return students, debts, retakes


def save_students(
    students: dict[str, dict[str, Any]],
    data_dir: str | Path = DEFAULT_DATA_DIR,
) -> None:
    save_json(Path(data_dir) / STUDENTS_FILE, students)


def save_debts(
    debts: list[dict[str, Any]],
    data_dir: str | Path = DEFAULT_DATA_DIR,
) -> None:
    save_json(Path(data_dir) / DEBTS_FILE, debts)


def save_retakes(
    retakes: list[dict[str, Any]],
    data_dir: str | Path = DEFAULT_DATA_DIR,
) -> None:
    save_json(Path(data_dir) / RETAKES_FILE, retakes)


def save_data(
    data_dir: str | Path,
    students: dict[str, dict[str, Any]],
    debts: list[dict[str, Any]],
    retakes: list[dict[str, Any]],
) -> None:
    save_students(students, data_dir)
    save_debts(debts, data_dir)
    save_retakes(retakes, data_dir)
