from django.urls import path

from . import views


app_name = "debts"


urlpatterns = [
    path("", views.debts, name="list"),
    path("<str:debt_id>/", views.debt_detail, name="detail"),
]
