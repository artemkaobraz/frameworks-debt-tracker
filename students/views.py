from django.conf import settings
from django.shortcuts import render

from models.debts import count_debts
from storage import load_data


def _data():
    return load_data(settings.BASE_DIR / "data")


def students(request):
    students_list, _, debts_list, _ = _data()
    student_rows = [
        {"student": student, "debt_count": count_debts(student, debts_list)}
        for student in students_list
    ]
    return render(
        request,
        "students/student_list.html",
        {"student_rows": student_rows},
    )


def student_detail(request, student_id):
    students_list, _, debts_list, _ = _data()
    student = next(
        (item for item in students_list if item.id == student_id),
        None,
    )
    if student is None:
        return render(
            request,
            "students/student_detail.html",
            {"student": None},
            status=404,
        )

    student_debts = [
        debt for debt in debts_list if debt.student.id == student.id
    ]
    return render(
        request,
        "students/student_detail.html",
        {
            "student": student,
            "student_debts": student_debts,
            "debt_count": count_debts(student, debts_list),
        },
    )
