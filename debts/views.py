from datetime import date

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render
from django.views.generic import CreateView, DeleteView, UpdateView

from students.models import Student

from .models import Debt


class DebtCreateView(CreateView):
    model = Debt
    fields = ["student", "discipline", "date_created", "is_closed"]
    template_name = "debts/debt_form.html"
    success_url = "/debts/"


class DebtUpdateView(UpdateView):
    model = Debt
    fields = ["student", "discipline", "date_created", "is_closed"]
    template_name = "debts/debt_form.html"
    success_url = "/debts/"


class DebtDeleteView(DeleteView):
    model = Debt
    template_name = "debts/debt_confirm_delete.html"
    success_url = "/debts/"


def debts(request):
    queryset = Debt.objects.select_related("student", "discipline")
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    discipline = request.GET.get("discipline", "").strip()
    student_id = request.GET.get("student_id", "").strip()
    discipline_id = request.GET.get("discipline_id", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    if query:
        queryset = queryset.filter(
            Q(student__name__icontains=query)
            | Q(discipline__name__icontains=query)
        )
    if status == "open":
        queryset = queryset.open()
    elif status == "closed":
        queryset = queryset.closed()
    if discipline:
        queryset = queryset.filter(discipline__name__icontains=discipline)
    if student_id.isdecimal() and len(student_id) <= 18:
        queryset = queryset.filter(student_id=int(student_id))
    if discipline_id.isdecimal() and len(discipline_id) <= 18:
        queryset = queryset.filter(discipline_id=int(discipline_id))
    for value, lookup in (
        (date_from, "date_created__gte"),
        (date_to, "date_created__lte"),
    ):
        try:
            parsed_date = date.fromisoformat(value)
        except ValueError:
            continue
        queryset = queryset.filter(**{lookup: parsed_date})
    sort = request.GET.get("sort", "date")
    ordering = {
        "date": ("date_created", "id"),
        "date_desc": ("-date_created", "-id"),
        "student": ("student__name", "date_created", "id"),
        "discipline": ("discipline__name", "date_created", "id"),
    }
    queryset = queryset.order_by(*ordering.get(sort, ordering["date"]))
    page = Paginator(queryset, 10).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(
        request, "debts/debt_list.html",
        {"debts": page, "page": page, "query": query, "status": status,
         "discipline": discipline, "sort": sort,
         "student_id": student_id, "discipline_id": discipline_id,
         "date_from": date_from, "date_to": date_to,
         "page_query": params.urlencode()},
    )


def debt_detail(request, debt_id):
    debt = Debt.objects.select_related("student", "discipline").filter(
        pk=debt_id
    ).first()
    return render(
        request, "debts/debt_detail.html", {"debt": debt},
        status=404 if debt is None else 200,
    )


def statistics(request):
    stats = Student.objects.annotate(
        debts_count=Count("debts", filter=Q(debts__is_closed=False))
    ).filter(debts_count__gt=0).order_by("-debts_count", "name")
    totals = Debt.objects.open().aggregate(total=Count("id"))
    return render(
        request, "debts/statistics.html",
        {"statistics": stats, "total_debts": totals["total"]},
    )
