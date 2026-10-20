from django.shortcuts import render

from db.database import get_connection


DISCIPLINES_SQL = """
SELECT id, name, teacher, semester FROM disciplines ORDER BY name
"""


def index(request):
    return render(request, "homepage/index.html")


def disciplines(request):
    connection = get_connection()
    try:
        disciplines_list = connection.execute(DISCIPLINES_SQL).fetchall()
    finally:
        connection.close()
    return render(
        request,
        "homepage/disciplines.html",
        {"disciplines": disciplines_list},
    )


def page_not_found(request, exception):
    return render(request, "homepage/404.html", status=404)
