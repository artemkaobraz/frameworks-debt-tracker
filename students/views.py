from django.shortcuts import render

from db.database import get_connection


STUDENTS_SQL = """
SELECT students.id, students.name, students.group_number,
       COUNT(debts.id) AS debts_count
FROM students
LEFT JOIN debts ON students.id = debts.student_id AND debts.is_closed = 0
GROUP BY students.id, students.name, students.group_number
ORDER BY students.name
"""
STUDENT_SQL = """
SELECT id, name, group_number, record_book FROM students WHERE id = ?
"""
STUDENT_DEBTS_SQL = """
SELECT debts.id, disciplines.name AS discipline_name, debts.is_closed
FROM debts
JOIN disciplines ON debts.discipline_id = disciplines.id
WHERE debts.student_id = ?
ORDER BY debts.date_created, debts.id
"""
ACTIVE_DEBTS_COUNT_SQL = """
SELECT COUNT(*) AS debts_count
FROM debts
WHERE student_id = ? AND is_closed = 0
"""
CLEAN_STUDENTS_SQL = """
SELECT id, name, group_number
FROM students
WHERE id NOT IN (SELECT student_id FROM debts WHERE is_closed = 0)
ORDER BY name
"""


def students(request):
    connection = get_connection()
    try:
        students_list = connection.execute(STUDENTS_SQL).fetchall()
    finally:
        connection.close()
    return render(
        request,
        "students/student_list.html",
        {"students": students_list},
    )


def student_detail(request, student_id):
    connection = get_connection()
    try:
        student = connection.execute(
            STUDENT_SQL, (student_id,)
        ).fetchone()
        if student is None:
            student_debts = []
            debt_count = 0
        else:
            student_debts = connection.execute(
                STUDENT_DEBTS_SQL, (student_id,)
            ).fetchall()
            debt_count = connection.execute(
                ACTIVE_DEBTS_COUNT_SQL, (student_id,)
            ).fetchone()["debts_count"]
    finally:
        connection.close()
    return render(
        request,
        "students/student_detail.html",
        {
            "student": student,
            "student_debts": student_debts,
            "debt_count": debt_count,
        },
        status=404 if student is None else 200,
    )


def clean_students(request):
    connection = get_connection()
    try:
        clean = connection.execute(CLEAN_STUDENTS_SQL).fetchall()
    finally:
        connection.close()
    return render(
        request,
        "students/clean_students.html",
        {"students": clean},
    )
