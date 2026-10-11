from django.conf import settings
from django.shortcuts import render

from storage import load_data


def _data():
    return load_data(settings.BASE_DIR / "data")


def debts(request):
    _, _, debts_list, _ = _data()
    return render(request, "debts/debt_list.html", {"debts": debts_list})


def debt_detail(request, debt_id):
    _, _, debts_list, _ = _data()
    debt = next((item for item in debts_list if item.id == debt_id), None)
    if debt is None:
        return render(
            request,
            "debts/debt_detail.html",
            {"debt": None},
            status=404,
        )

    return render(
        request,
        "debts/debt_detail.html",
        {"debt": debt},
    )
