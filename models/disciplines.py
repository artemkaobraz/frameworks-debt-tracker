from typing import Any


class Discipline:
    def __init__(
        self,
        id: str,
        name: str,
        teacher: str = "",
        semester: int = 0,
    ) -> None:
        self.id = _required(id, "ID дисциплины")
        self.name = _required(name, "Название дисциплины")
        self.teacher = teacher.strip()
        self.semester = int(semester)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> "Discipline":
        return cls(
            str(data["id"]),
            str(data["name"]),
            str(data.get("teacher", "")),
            int(data.get("semester", 0)),
        )

    def to_data(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "teacher": self.teacher,
            "semester": self.semester,
        }


def _required(value: object, field: str) -> str:
    result = str(value).strip()
    if not result:
        raise ValueError(f'Поле "{field}" не может быть пустым')
    return result


def add_discipline(
    disciplines: list[Discipline],
    discipline_id: object,
    name: str,
    teacher: str = "",
    semester: int = 0,
) -> Discipline:
    key = _required(discipline_id, "ID дисциплины")
    if any(item.id == key for item in disciplines):
        raise ValueError(f"Дисциплина с ID {key} уже существует")
    discipline = Discipline(key, name, teacher, semester)
    disciplines.append(discipline)
    return discipline


def get_discipline(
    disciplines: list[Discipline],
    discipline_id: object,
) -> Discipline:
    key = _required(discipline_id, "ID дисциплины")
    for discipline in disciplines:
        if discipline.id == key:
            return discipline
    raise KeyError(f"Дисциплина с ID {key} не найдена")
