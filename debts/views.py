from django.shortcuts import render

from db.database import get_connection


DEBTS_SQL = """
SELECT debts.id, students.name AS student_name,
       disciplines.name AS discipline_name, debts.date_created,
       debts.is_closed
FROM debts
JOIN students ON debts.student_id = students.id
JOIN disciplines ON debts.discipline_id = disciplines.id
ORDER BY debts.date_created, debts.id
"""
DEBT_SQL = """
SELECT debts.id, students.id AS student_id,
       students.name AS student_name,
       disciplines.name AS discipline_name, debts.date_created,
       debts.is_closed
FROM debts
JOIN students ON debts.student_id = students.id
JOIN disciplines ON debts.discipline_id = disciplines.id
WHERE debts.id = ?
"""
STATISTICS_SQL = """
SELECT students.name AS student_name, COUNT(debts.id) AS debts_count
FROM students
LEFT JOIN debts ON students.id = debts.student_id AND debts.is_closed = 0
GROUP BY students.id, students.name
ORDER BY debts_count DESC, students.name
"""


def debts(request):
    connection = get_connection()
    try:
        debts_list = connection.execute(DEBTS_SQL).fetchall()
    finally:
        connection.close()
    return render(request, "debts/debt_list.html", {"debts": debts_list})


def debt_detail(request, debt_id):
    connection = get_connection()
    try:
        debt = connection.execute(DEBT_SQL, (debt_id,)).fetchone()
    finally:
        connection.close()
    return render(
        request,
        "debts/debt_detail.html",
        {"debt": debt},
        status=404 if debt is None else 200,
    )


def statistics(request):
    connection = get_connection()
    try:
        stats = connection.execute(STATISTICS_SQL).fetchall()
    finally:
        connection.close()
    return render(
        request,
        "debts/statistics.html",
        {"statistics": stats},
    )
