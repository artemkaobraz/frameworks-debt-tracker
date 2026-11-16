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
    if query:
        queryset = queryset.filter(
            Q(student__name__icontains=query)
            | Q(discipline__name__icontains=query)
        )
    if status in {"open", "closed"}:
        queryset = queryset.filter(is_closed=status == "closed")
    if discipline:
        queryset = queryset.filter(discipline__name__icontains=discipline)
    sort = request.GET.get("sort", "date")
    ordering = {
        "date": ("date_created", "id"),
        "student": ("student__name", "date_created", "id"),
    }
    queryset = queryset.order_by(*ordering.get(sort, ordering["date"]))
    page = Paginator(queryset, 10).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(
        request, "debts/debt_list.html",
        {"debts": page, "page": page, "query": query, "status": status,
         "discipline": discipline, "sort": sort,
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
    ).order_by("-debts_count", "name")
    totals = Debt.objects.aggregate(total=Count("id"))
    return render(
        request, "debts/statistics.html",
        {"statistics": stats, "total_debts": totals["total"]},
    )
