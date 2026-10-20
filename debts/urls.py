from django.urls import path

from . import views


app_name = "debts"


urlpatterns = [
    path("", views.debts, name="list"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:debt_id>/", views.debt_detail, name="detail"),
]
