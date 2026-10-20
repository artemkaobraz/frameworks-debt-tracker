from pathlib import Path

from db.database import DB_PATH, PROJECT_ROOT, get_connection
from storage import load_data


DATA_DIR = PROJECT_ROOT / "data"
SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"
DELETE_DEBTS_SQL = "DELETE FROM debts"
DELETE_DISCIPLINES_SQL = "DELETE FROM disciplines"
DELETE_STUDENTS_SQL = "DELETE FROM students"
INSERT_STUDENT_SQL = """
INSERT INTO students (id, name, group_number, record_book)
VALUES (?, ?, ?, ?)
"""
INSERT_DISCIPLINE_SQL = """
INSERT INTO disciplines (id, name, teacher, semester)
VALUES (?, ?, ?, ?)
"""
INSERT_DEBT_SQL = """
INSERT INTO debts (
    id, student_id, discipline_id, date_created, is_closed
)
VALUES (?, ?, ?, ?, ?)
"""
REQUIRED_TABLES = {"students", "disciplines", "debts"}
TABLES_SQL = """
SELECT name FROM sqlite_master
WHERE type = ? AND name IN (?, ?, ?)
"""


def _integer_id(value, entity):
    try:
        identifier = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"{entity}: идентификатор должен быть целым числом"
        ) from error
    if identifier <= 0:
        raise ValueError(
            f"{entity}: идентификатор должен быть положительным"
        )
    return identifier


def _prepare_rows(data_dir):
    students, disciplines, debts, _ = load_data(Path(data_dir))
    student_rows = [
        (
            _integer_id(student.id, "student"),
            student.name,
            student.group_number,
            student.record_book,
        )
        for student in students
    ]
    discipline_rows = [
        (
            _integer_id(discipline.id, "discipline"),
            discipline.name,
            discipline.teacher,
            discipline.semester,
        )
        for discipline in disciplines
    ]
    debt_rows = [
        (
            _integer_id(debt.id, "debt"),
            _integer_id(debt.student.id, "student"),
            _integer_id(debt.discipline.id, "discipline"),
            debt.date_created,
            int(debt.is_closed),
        )
        for debt in debts
    ]
    student_ids = {row[0] for row in student_rows}
    discipline_ids = {row[0] for row in discipline_rows}
    for _, student_id, discipline_id, _, _ in debt_rows:
        if student_id not in student_ids:
            raise ValueError("debt: ссылка на отсутствующего студента")
        if discipline_id not in discipline_ids:
            raise ValueError("debt: ссылка на отсутствующую дисциплину")
    return student_rows, discipline_rows, debt_rows


def _initialize_schema(connection, schema):
    tables = {
        row["name"]
        for row in connection.execute(
            TABLES_SQL,
            ("table", "students", "disciplines", "debts"),
        )
    }
    if not tables:
        connection.executescript(schema)
    elif tables != REQUIRED_TABLES:
        raise ValueError("структура базы данных неполна")


def import_data(connection, data_dir=DATA_DIR, schema_path=SCHEMA_PATH):
    student_rows, discipline_rows, debt_rows = _prepare_rows(data_dir)
    schema = Path(schema_path).read_text(encoding="utf-8")
    _initialize_schema(connection, schema)
    try:
        connection.execute("BEGIN")
        connection.execute(DELETE_DEBTS_SQL)
        connection.execute(DELETE_DISCIPLINES_SQL)
        connection.execute(DELETE_STUDENTS_SQL)
        connection.executemany(
            INSERT_STUDENT_SQL,
            student_rows,
        )
        connection.executemany(
            INSERT_DISCIPLINE_SQL,
            discipline_rows,
        )
        connection.executemany(
            INSERT_DEBT_SQL,
            debt_rows,
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def main(database_path=DB_PATH, data_dir=DATA_DIR):
    connection = get_connection(database_path)
    try:
        import_data(connection, data_dir)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
