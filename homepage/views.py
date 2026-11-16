from django.shortcuts import render
from django.views.generic import CreateView, DeleteView, UpdateView

from .models import Discipline


class DisciplineCreateView(CreateView):
    model = Discipline
    fields = ["name", "teacher", "semester"]
    template_name = "homepage/discipline_form.html"
    success_url = "/disciplines/"


class DisciplineUpdateView(UpdateView):
    model = Discipline
    fields = ["name", "teacher", "semester"]
    template_name = "homepage/discipline_form.html"
    success_url = "/disciplines/"


class DisciplineDeleteView(DeleteView):
    model = Discipline
    template_name = "homepage/discipline_confirm_delete.html"
    success_url = "/disciplines/"


def index(request):
    return render(request, "homepage/index.html")


def disciplines(request):
    queryset = Discipline.objects.all()
    query = request.GET.get("q", "").strip()
    semester = request.GET.get("semester", "").strip()
    if query:
        queryset = queryset.filter(name__icontains=query)
    if semester.isdigit():
        queryset = queryset.filter(semester=int(semester))
    queryset = queryset.order_by("name", "id")
    return render(
        request, "homepage/disciplines.html",
        {"disciplines": queryset, "query": query, "semester": semester},
    )


def page_not_found(request, exception):
    return render(request, "homepage/404.html", status=404)
