from django.db.models import Count, Q
from django.shortcuts import render
from django.views.generic import CreateView, DeleteView, UpdateView

from .models import Student


class StudentCreateView(CreateView):
    model = Student
    fields = ["name", "group_number", "record_book"]
    template_name = "students/student_form.html"
    success_url = "/students/"


class StudentUpdateView(UpdateView):
    model = Student
    fields = ["name", "group_number", "record_book"]
    template_name = "students/student_form.html"
    success_url = "/students/"


class StudentDeleteView(DeleteView):
    model = Student
    template_name = "students/student_confirm_delete.html"
    success_url = "/students/"


def students(request):
    queryset = Student.objects.annotate(
        debts_count=Count("debts", filter=Q(debts__is_closed=False))
    )
    query = request.GET.get("q", "").strip()
    group = request.GET.get("group", "").strip()
    discipline = request.GET.get("discipline", "").strip()
    if query:
        queryset = queryset.filter(name__icontains=query)
    if group:
        queryset = queryset.filter(group_number=group)
    if discipline:
        queryset = queryset.filter(
            debts__discipline__name__icontains=discipline
        ).distinct()
    sort = request.GET.get("sort", "name")
    ordering = {
        "name": ("name", "id"),
        "debt_count": ("-debts_count", "name", "id"),
    }
    queryset = queryset.order_by(*ordering.get(sort, ordering["name"]))
    return render(
        request, "students/student_list.html",
        {"students": queryset, "query": query, "group": group,
         "discipline": discipline, "sort": sort},
    )


def student_detail(request, student_id):
    student = Student.objects.filter(pk=student_id).first()
    if student is None:
        student_debts = []
        debt_count = 0
    else:
        student_debts = student.debts.select_related("discipline").order_by(
            "date_created", "id"
        )
        debt_count = student.debts.filter(is_closed=False).count()
    return render(
        request, "students/student_detail.html",
        {"student": student, "student_debts": student_debts,
         "debt_count": debt_count},
        status=404 if student is None else 200,
    )


def clean_students(request):
    clean = Student.objects.exclude(
        debts__is_closed=False
    ).distinct().order_by("name", "id")
    return render(
        request, "students/clean_students.html", {"students": clean}
    )
