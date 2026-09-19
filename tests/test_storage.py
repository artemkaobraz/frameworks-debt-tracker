import pytest

from storage import load_data
from storage import load_json


def test_load_json_returns_default_for_missing_file(tmp_path) -> None:
    default = {"items": []}

    result = load_json(tmp_path / "missing.json", default)

    assert result == default
    assert result is not default


def test_load_json_rejects_invalid_json(tmp_path) -> None:
    file_path = tmp_path / "broken.json"
    file_path.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(ValueError):
        load_json(file_path, {})


def test_load_data_rejects_wrong_root_type(tmp_path) -> None:
    students_file = tmp_path / "students.json"
    students_file.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError):
        load_data(tmp_path)
