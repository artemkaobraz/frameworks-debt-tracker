import sqlite3
from pathlib import Path

import pytest

from db.database import PROJECT_ROOT, get_connection
from db.import_json import import_data


EXPECTED_COUNTS = {
    "students": 3,
    "disciplines": 2,
    "debts": 3,
}
COUNT_QUERIES = {
    "students": "SELECT COUNT(*) FROM students",
    "disciplines": "SELECT COUNT(*) FROM disciplines",
    "debts": "SELECT COUNT(*) FROM debts",
}


def _query_statements(path):
    statements = []
    buffer = ""
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("--"):
            continue
        buffer += line + "\n"
        if sqlite3.complete_statement(buffer):
            statements.append(buffer.strip())
            buffer = ""
    assert not buffer.strip()
    return statements


def test_schema_foreign_keys_and_imported_data() -> None:
    connection = get_connection()
    try:
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = ?",
                ("table",),
            )
        }
        foreign_keys = connection.execute(
            "PRAGMA foreign_key_list(debts)"
        ).fetchall()
        counts = {
            table: connection.execute(query).fetchone()[0]
            for table, query in COUNT_QUERIES.items()
        }
        student = connection.execute(
            "SELECT name, group_number FROM students WHERE id = ?", (1,)
        ).fetchone()
        integrity = connection.execute("PRAGMA foreign_key_check").fetchall()
    finally:
        connection.close()

    assert tables == {"students", "disciplines", "debts"}
    assert {row["table"] for row in foreign_keys} == {
        "students", "disciplines"
    }
    assert counts == EXPECTED_COUNTS
    assert tuple(student) == ("Анна Смирнова", "ЭФБО-02-24")
    assert integrity == []


def test_import_is_repeatable_and_works_with_missing_disciplines_file(
    tmp_path,
) -> None:
    database_path = tmp_path / "test.sqlite"
    connection = get_connection(database_path)
    try:
        import_data(connection, PROJECT_ROOT / "data")
        import_data(connection, PROJECT_ROOT / "data")
        counts = {
            table: connection.execute(query).fetchone()[0]
            for table, query in COUNT_QUERIES.items()
        }
    finally:
        connection.close()

    assert not (PROJECT_ROOT / "data" / "disciplines.json").exists()
    assert counts == EXPECTED_COUNTS


def test_failed_import_preserves_existing_database(tmp_path) -> None:
    database_path = tmp_path / "test.sqlite"
    connection = get_connection(database_path)
    try:
        import_data(connection, PROJECT_ROOT / "data")
        before = connection.execute(
            "SELECT id, name FROM students ORDER BY id"
        ).fetchall()
        connection.execute(
            """
            CREATE TRIGGER reject_student_import
            BEFORE INSERT ON students
            BEGIN
                SELECT RAISE(ABORT, 'injected import failure');
            END
            """
        )
        connection.commit()

        with pytest.raises(sqlite3.IntegrityError):
            import_data(connection, PROJECT_ROOT / "data")

        after = connection.execute(
            "SELECT id, name FROM students ORDER BY id"
        ).fetchall()
        counts = {
            table: connection.execute(query).fetchone()[0]
            for table, query in COUNT_QUERIES.items()
        }
    finally:
        connection.close()

    assert [tuple(row) for row in after] == [tuple(row) for row in before]
    assert counts == EXPECTED_COUNTS


def test_all_documented_queries_execute() -> None:
    statements = _query_statements(PROJECT_ROOT / "sql" / "queries.sql")
    connection = get_connection()
    try:
        results = [connection.execute(statement).fetchall()
                   for statement in statements]
    finally:
        connection.close()

    assert len(statements) == 12
    assert all(result is not None for result in results)
