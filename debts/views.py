from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, UpdateView

from students.models import Student

from .forms import DebtFilterForm, DebtForm
from .models import Debt


class DebtCreateView(CreateView):
    model = Debt
    form_class = DebtForm
    template_name = "debts/debt_form.html"
    success_url = "/debts/"


class DebtUpdateView(UpdateView):
    model = Debt
    form_class = DebtForm
    template_name = "debts/debt_form.html"
    success_url = "/debts/"


class DebtDeleteView(DeleteView):
    model = Debt
    template_name = "debts/debt_confirm_delete.html"
    success_url = "/debts/"


def debts(request):
    queryset = Debt.objects.select_related("student", "discipline")
    filter_form = DebtFilterForm(request.GET or None)
    sort = "date"
    if filter_form.is_valid():
        filters = filter_form.cleaned_data
        query = filters["q"].strip()
        if query:
            queryset = queryset.filter(
                Q(student__name__icontains=query)
                | Q(discipline__name__icontains=query)
            )
        if filters["status"] == "open":
            queryset = queryset.open()
        elif filters["status"] == "closed":
            queryset = queryset.closed()
        if filters["discipline"]:
            queryset = queryset.filter(
                discipline__name__icontains=filters["discipline"].strip()
            )
        if filters["student_id"]:
            queryset = queryset.filter(student_id=filters["student_id"])
        if filters["discipline_id"]:
            queryset = queryset.filter(
                discipline_id=filters["discipline_id"]
            )
        if filters["date_from"]:
            queryset = queryset.filter(
                date_created__gte=filters["date_from"]
            )
        if filters["date_to"]:
            queryset = queryset.filter(date_created__lte=filters["date_to"])
        sort = filters["sort"] or sort
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
        {"debts": page, "page": page, "filter_form": filter_form,
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


@require_POST
def close_debt(request, debt_id):
    debt = get_object_or_404(Debt, pk=debt_id)
    if not debt.is_closed:
        debt.is_closed = True
        debt.save(update_fields=["is_closed"])
    return redirect("debts:detail", debt_id=debt_id)


def statistics(request):
    stats = Student.objects.annotate(
        debts_count=Count("debts", filter=Q(debts__is_closed=False))
    ).filter(debts_count__gt=0).order_by("-debts_count", "name")
    totals = Debt.objects.open().aggregate(total=Count("id"))
    return render(
        request, "debts/statistics.html",
        {"statistics": stats, "total_debts": totals["total"]},
    )
