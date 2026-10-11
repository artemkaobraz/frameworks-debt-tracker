from django.conf import settings
from django.shortcuts import render

from storage import load_data


def index(request):
    return render(request, "homepage/index.html")


def disciplines(request):
    _, disciplines_list, _, _ = load_data(settings.BASE_DIR / "data")
    return render(
        request,
        "homepage/disciplines.html",
        {"disciplines": disciplines_list},
    )


def page_not_found(request, exception):
    return render(request, "homepage/404.html", status=404)
