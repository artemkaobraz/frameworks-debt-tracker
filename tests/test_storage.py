import json

import pytest

from models.debts import Debt
from models.disciplines import Discipline
from models.retakes import Retake
from models.students import Student
from storage import load_data
from storage import load_json
from storage import save_data


def _write_json(path, data: object) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8",
    )


def test_load_json_returns_default_for_missing_file(tmp_path) -> None:
    default = {"items": []}

    result = load_json(tmp_path / "missing.json", default)

    assert result == default
    assert result is not default


def test_load_json_rejects_invalid_json(tmp_path) -> None:
    file_path = tmp_path / "broken.json"
    file_path.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(ValueError, match="Некорректный JSON"):
        load_json(file_path, {})


def test_load_data_rejects_malformed_json(tmp_path) -> None:
    (tmp_path / "debts.json").write_text("[}", encoding="utf-8")

    with pytest.raises(ValueError, match="debts.json"):
        load_data(tmp_path)


def test_load_data_rejects_wrong_root_type(tmp_path) -> None:
    _write_json(tmp_path / "students.json", [])

    with pytest.raises(ValueError, match="ожидался объект JSON"):
        load_data(tmp_path)


def test_save_and_load_preserve_object_graph(tmp_path) -> None:
    student = Student("10", "Анна Смирнова", "ЭФБО-02-24", "12345")
    discipline = Discipline("20", "Математика", "И. И. Иванов", 3)
    debt = Debt("30", student, discipline, "2026-09-01")
    retake = Retake("40", debt, "2026-09-25", "назначена")

    save_data(
        tmp_path,
        [student],
        [discipline],
        [debt],
        [retake],
    )
    students, disciplines, debts, retakes = load_data(tmp_path)

    assert debts[0].student is students[0]
    assert debts[0].discipline is disciplines[0]
    assert retakes[0].debt is debts[0]
    assert retakes[0].debt.student.name == "Анна Смирнова"


def test_save_data_uses_new_schema_with_ids(tmp_path) -> None:
    student = Student("1", "Илья Петров", "ЭФБО-02-24", "54321")
    discipline = Discipline("2", "Информатика", "П. П. Петров", 2)
    debt = Debt("3", student, discipline, "2026-09-03")
    retake = Retake("4", debt, "2026-09-28")

    save_data(
        tmp_path,
        [student],
        [discipline],
        [debt],
        [retake],
    )

    students_data = load_json(tmp_path / "students.json", {})
    disciplines_data = load_json(tmp_path / "disciplines.json", [])
    debts_data = load_json(tmp_path / "debts.json", [])
    retakes_data = load_json(tmp_path / "retakes.json", [])
    assert students_data == {
        "1": {
            "name": "Илья Петров",
            "group_number": "ЭФБО-02-24",
            "record_book": "54321",
        }
    }
    assert disciplines_data[0]["id"] == "2"
    assert debts_data[0]["student_id"] == "1"
    assert debts_data[0]["discipline_id"] == "2"
    assert "discipline" not in debts_data[0]
    assert retakes_data[0]["debt_id"] == "3"
    assert "student_id" not in retakes_data[0]


def test_load_data_migrates_legacy_schema(tmp_path) -> None:
    _write_json(
        tmp_path / "students.json",
        {
            "7": {
                "full_name": "Мария Волкова",
                "group": "ЭФБО-02-24",
            }
        },
    )
    _write_json(
        tmp_path / "debts.json",
        [
            {
                "student_id": "7",
                "discipline": "Физика",
                "created_at": "2026-08-20",
                "status": "open",
            }
        ],
    )
    _write_json(
        tmp_path / "retakes.json",
        [
            {
                "student_id": "7",
                "discipline": "Физика",
                "retake_date": "2026-09-30",
            }
        ],
    )

    students, disciplines, debts, retakes = load_data(tmp_path)

    assert students[0].id == "7"
    assert students[0].name == "Мария Волкова"
    assert students[0].record_book == ""
    assert disciplines[0].id == "1"
    assert disciplines[0].name == "Физика"
    assert debts[0].id == "1"
    assert debts[0].student is students[0]
    assert debts[0].discipline is disciplines[0]
    assert retakes[0].id == "1"
    assert retakes[0].debt is debts[0]


@pytest.mark.parametrize(
    ("file_name", "data"),
    [
        (
            "debts.json",
            [
                {
                    "id": "1",
                    "student_id": "missing",
                    "discipline_id": "1",
                    "date_created": "2026-09-01",
                    "is_closed": False,
                }
            ],
        ),
        (
            "retakes.json",
            [
                {
                    "id": "1",
                    "debt_id": "missing",
                    "retake_date": "2026-09-25",
                }
            ],
        ),
    ],
)
def test_load_data_rejects_dangling_references(
    tmp_path,
    file_name: str,
    data: object,
) -> None:
    _write_json(
        tmp_path / "students.json",
        {"1": {"name": "Анна", "group_number": "ЭФБО-02-24"}},
    )
    _write_json(
        tmp_path / "disciplines.json",
        [{"id": "1", "name": "Математика"}],
    )
    if file_name == "retakes.json":
        _write_json(tmp_path / "debts.json", [])
    _write_json(tmp_path / file_name, data)

    with pytest.raises(ValueError, match="недействительная ссылка"):
        load_data(tmp_path)
